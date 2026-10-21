#!/usr/bin/env python3
"""Check tracked release files for accidental local data and common secret shapes.

Heuristics are not a guarantee. Review every staged file and publication history.
Run from any directory in a Git checkout; only paths, not matches, are printed.
"""
import argparse
import hashlib
from pathlib import Path
import re
import subprocess
import sys


RULES = {
    'private key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'GitHub token': r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b',
    'cloud access key': r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'provider token': r'\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{30,}\b',
    'credential in URL': r'https?://[^\s/]+:[^\s/@]+@',
    'Mac/Linux user path': r'/(?:Users|home)/[A-Za-z0-9_.-]+/',
    'Windows user path': r'[A-Za-z]:[\\/]Users[\\/][^\s\\/]+[\\/]',
}
FORBIDDEN = {'.env', '.pem', '.key', '.db', '.sqlite', '.sqlite3', '.jsonl',
             '.log', '.mp4', '.mov', '.mp3', '.wav', '.gguf', '.safetensors', '.zip'}
LOCAL_DOCUMENTS = {'docs/social-posts.md', 'docs/reddit-posts.md'}

# Reviewed logo and explanatory graphics are pinned, rather than allowing arbitrary
# binaries. Updating them requires reviewing provenance and the actual pixels.
VERIFIED_ASSETS = {
    'examples/demo-vault/Assets/UPHASH/logo.png':
        '411d66c2838348f7b0715b9d7fa435263acabda2d1d8e2e299a81ac00848b799',
    'docs/assets/agent-kit-v0.1.2-en.png':
        '8b8936b5b4df0da646338685aff61a4fe80af53027e42dd27502365d33fa896c',
    'docs/assets/agent-kit-v0.1.2-ja.png':
        'c3dca083b8c56c0edcea00f9157d46148a1ffa30b9e362d8e8f00a38908805ca',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deny-term', action='append', default=[],
                        help='Additional private term to reject; never printed')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
    paths = [p for p in paths if p]
    if not paths:
        print('FAIL: no tracked files; stage the exact release set first')
        return 1
    failures = []
    for relative in paths:
        path = root / relative
        if relative in LOCAL_DOCUMENTS or 'drafts' in Path(relative).parts or path.name.endswith('.draft.md'):
            failures.append((relative, 'local-only publication draft'))
            continue
        if path.is_symlink():
            failures.append((relative, 'symlink'))
            continue
        if path.suffix.lower() in FORBIDDEN or path.name.startswith('.env') or path.name == 'config.json':
            failures.append((relative, 'local/private file type'))
        if any(p in {'.serena', '.local', 'node_modules', '__pycache__', '.venv'} for p in path.parts):
            failures.append((relative, 'local directory'))
        raw = path.read_bytes()
        if relative in VERIFIED_ASSETS:
            if hashlib.sha256(raw).hexdigest() != VERIFIED_ASSETS[relative]:
                failures.append((relative, 'unreviewed brand asset'))
            continue
        if len(raw) > 200_000 or b'\0' in raw:
            failures.append((relative, 'large/binary payload'))
            continue
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            failures.append((relative, 'non UTF-8 payload'))
            continue
        for label, pattern in RULES.items():
            if re.search(pattern, text):
                failures.append((relative, label))
        if any(term.casefold() in text.casefold() for term in args.deny_term):
            failures.append((relative, 'private term'))
    for path, reason in failures:
        print('FAIL ' + path + ': ' + reason)
    print(f'{"FAIL" if failures else "PASS"}: reviewed {len(paths)} tracked files (text checks and pinned brand asset hashes)')
    return int(bool(failures))


if __name__ == '__main__':
    sys.exit(main())
