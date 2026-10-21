#!/usr/bin/env python3
# Copyright (c) 2026 UPHASH Inc. SPDX-License-Identifier: MIT
"""Read scoped Markdown once; suppress unchanged bodies using caller-held hashes.

No network, writes, transcript access, background process, or persistent cache.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

VERSION = '0.1.2'

def config_path():
    return Path(os.environ.get('OBSIDIAN_CONTEXT_CONFIG',
                str(Path.home() / '.config/obsidian-context/config.json'))).expanduser()

def load_config(path):
    data = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    if not isinstance(data, dict) or data.get('version') != 1 or not isinstance(data.get('scopes'), dict) or not data['scopes']:
        raise ValueError('Expected version: 1 and a non-empty scopes object')
    roots = []
    for scope, spec in data['scopes'].items():
        if not re.fullmatch(r'[a-z][a-z0-9_-]*', scope) or not isinstance(spec, dict):
            raise ValueError('Invalid scope name or definition')
        root = Path(spec['root']).expanduser()
        policy = Path(spec['policy'])
        if not root.is_absolute() or policy.is_absolute() or '..' in policy.parts or policy.suffix != '.md':
            raise ValueError('Vault root must be absolute; policy must be a relative Markdown path')
        root = root.resolve()
        if any(root.is_relative_to(r) or r.is_relative_to(root) for r in roots):
            raise ValueError('Scope roots must not overlap')
        roots.append(root)
        if spec.get('sync') not in ('local', 'git') or (scope == 'personal' and spec['sync'] != 'local'):
            raise ValueError('Use sync local or git; personal must stay local')
        if not isinstance(spec.get('owners', []), list) or not all(isinstance(x, str) for x in spec.get('owners', [])):
            raise ValueError('owners must be a list of names')
    return data

def confined(root, relative):
    if Path(relative).is_absolute() or '..' in Path(relative).parts:
        raise ValueError('Note paths must be relative, without parent traversal')
    p = (root / relative).resolve(strict=True)
    if p.suffix.lower() != '.md' or not p.is_relative_to(root.resolve()):
        raise ValueError('Only Markdown within the selected scope is allowed')
    if not p.is_file():
        raise ValueError('Not a regular note')
    return p

def stable_read(p):
    for _ in range(3):
        with p.open('rb') as f:
            a = os.fstat(f.fileno())
            raw = f.read()
            b = os.fstat(f.fileno())
            # Windows stat(path) and fstat(fd) can give different ctime meanings.
            # Reopen the path while holding the original handle to verify identity
            # and metadata using fstat consistently, without reading the body twice.
            # https://github.com/python/cpython/issues/157671
            with p.open('rb') as current:
                c = os.fstat(current.fileno())
        signature = lambda s: (s.st_dev, s.st_ino, s.st_mtime_ns, s.st_ctime_ns, s.st_size)
        if signature(a) == signature(b) == signature(c) and len(raw) == b.st_size:
            return raw, b
    raise OSError('Note changed during reading; retry before using it. Metadata: ' + repr((signature(a), signature(b), signature(c))))

def excerpt(text, limit, pattern):
    if len(text) <= limit and not pattern:
        return text, 'complete'
    lines = text.splitlines(keepends=True)
    selected = set()
    front_end = 0
    if lines and lines[0].strip() == '---':
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == '---'), 0)
        front_end = end + 1
        selected.update(range(front_end))
    headings, fence = [], None
    for i in range(front_end, len(lines)):
        line = lines[i]
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if fence:
            if (marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1]
                    and not marker[2].strip()):
                fence = None
            continue
        if marker:
            fence = (marker[1][0], len(marker[1]))
            continue
        heading = re.match(r'^(#{1,6})[ \t]+', line)
        if heading:
            headings.append((i, len(heading[1]), line.strip()))
    matcher = re.compile(pattern or r'要約|概要|現在|最新|決定|制約|方針|summary|current|decision|constraint', re.I)
    matched = False
    for n, (i, level, heading) in enumerate(headings):
        if matcher.search(heading):
            matched = True
            # A selected section includes its nested subsections, not just its preamble.
            end = next((j for j, depth, _ in headings[n + 1:] if depth <= level), len(lines))
            selected.update(range(i, end))
    toc = '\n'.join(h for _, _, h in headings)
    if not matched and pattern:
        body = ''.join(lines[i] for i in sorted(selected))[:limit]
        return body + '\n[PARTIAL: no heading matched; choose a matching --section.]\n' + toc[:1200], 'partial'
    if not matched:
        selected.update(range(len(lines)))
    body = ''.join(lines[i] for i in sorted(selected))
    truncated = len(body) > limit
    body = body[:limit]
    if not truncated and len(selected) == len(lines):
        return body, 'complete'
    if truncated:
        notice = '[PARTIAL: selected content truncated; increase --chars or narrow --section.]'
    elif pattern:
        # Known sections need no repeated full outline, which also spent later files' budget.
        notice = '[PARTIAL: selected sections complete; other sections omitted.]'
    else:
        notice = '[PARTIAL: inspect omitted headings when relevant]\n' + toc[:1200]
    return body + '\n' + notice, 'partial'

def run(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
        epilog='Obsidian Agent Kit by UPHASH | MIT | https://uphash.net/')
    ap.add_argument('scope', help='Scope defined in the local configuration')
    ap.add_argument('--config', type=Path, default=config_path(), help='Local configuration JSON')
    ap.add_argument('--version', action='version', version=VERSION)
    ap.add_argument('--compact', action='store_true', help='Omit mtime/size from output; keep full content hashes. Batch policy reads are not filtered by --section.')
    ap.add_argument('--query', help='Exact note stem preferred; otherwise filename candidates only')
    ap.add_argument('--check', action='append', default=[], metavar='RELATIVE_PATH=SHA256', help='Known path with digest retained in this conversation')
    ap.add_argument('--file', action='append', default=[], help='Read a known relative path without a baseline')
    ap.add_argument('--force', action='store_true', help='Recheck content despite matching hash: conflict, reported update, lost context, unread section')
    ap.add_argument('--section', help='Heading regex for a focused read; use --force for an already-read file')
    ap.add_argument('--chars', type=int, default=6000, help='Soft combined excerpt budget; raise for necessary context')
    args = ap.parse_args(argv)
    if args.chars < 100:
        ap.error('--chars must be at least 100')
    try:
        config = load_config(args.config)
        spec = config['scopes'][args.scope]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        ap.error('Cannot load scope configuration: ' + str(exc))
    root = Path(spec['root']).expanduser().resolve()
    if not root.is_dir():
        ap.error('Selected vault is missing or inaccessible')
    wanted = {p: None for p in args.file}
    for item in args.check:
        p, sep, digest = item.rpartition('=')
        if not sep or not re.fullmatch('[0-9a-f]{64}', digest):
            ap.error('--check requires relative path and a full SHA-256')
        wanted[p] = digest
    if args.query:
        policy = spec['policy']
        wanted.setdefault(policy, None)
        matches = []
        for p in root.rglob('*.md'):
            if args.query.casefold() not in p.stem.casefold() or any(x.startswith('.') for x in p.relative_to(root).parts):
                continue
            try:
                confined(root, p.relative_to(root))
            except (OSError, ValueError):
                continue
            matches.append(p)
        matches.sort()
        exact = [p for p in matches if p.stem.casefold() == args.query.casefold()]
        if len(exact) == 1:
            wanted.setdefault(exact[0].relative_to(root).as_posix(), None)
        else:
            print(json.dumps({'candidates': [p.relative_to(root).as_posix() for p in matches[:12]], 'more': len(matches) > 12}, ensure_ascii=False))
    if not wanted:
        ap.error('Supply --query, --file, or --check')
    errors = 0
    remaining = args.chars
    for relative, previous in wanted.items():
        try:
            p = confined(root, relative)
            raw, st = stable_read(p)
            digest = hashlib.sha256(raw).hexdigest()
            unchanged = digest == previous and not args.force
            header = {'path': relative, 'sha256': digest, 'mtime_ns': st.st_mtime_ns, 'size': st.st_size, 'status': 'UNCHANGED' if unchanged else 'CONTENT'}
            if args.compact:
                del header['mtime_ns'], header['size']
            if unchanged:
                print(json.dumps(header, ensure_ascii=False))
                continue
            pattern = args.section
            if args.compact and relative == spec['policy'] and len(wanted) > 1:
                pattern = None  # Project section names must not filter out the shared policy.
            body, coverage = excerpt(raw.decode('utf-8'), max(100, remaining), pattern)
            remaining -= len(body)
            header['coverage'] = coverage
            print(json.dumps(header, ensure_ascii=False))
            print(body.rstrip())
        except (OSError, ValueError, UnicodeError, re.error) as exc:
            errors += 1
            print(json.dumps({'path': relative, 'status': 'ERROR', 'error': str(exc)}, ensure_ascii=False))
    return 1 if errors else 0

if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    sys.exit(run())
