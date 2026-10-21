#!/usr/bin/env python3
# Copyright (c) 2026 UPHASH Inc. SPDX-License-Identifier: MIT
"""Create an isolated, fictional demo. Never changes global AI settings."""
import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import sys

from setup import rendered_rule

SOURCE = Path(__file__).resolve().parent
NOTE = 'Projects/Lighthouse.md'
MARKER = '.obsidian-agent-kit-demo.json'


def init_demo(dest):
    # Refuse to mix demo files into an existing directory or vault.
    dest.mkdir(parents=True, exist_ok=False)
    shutil.copytree(SOURCE / 'examples/demo-vault', dest / 'vault')
    shutil.copyfile(SOURCE / 'obsidian_context.py', dest / 'obsidian_context.py')
    shutil.copyfile(SOURCE / 'LICENSE', dest / 'LICENSE')
    config = {'version': 1, 'scopes': {'demo': {
        'root': str(dest / 'vault'), 'policy': 'Policies/Knowledge policy.md',
        'sync': 'local', 'owners': []}}}
    config_path = dest / 'config.json'
    config_path.write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')
    parts = [sys.executable, str(dest / 'obsidian_context.py'), '--config', str(config_path)]
    if os.name == 'nt':
        command = '& ' + ' '.join("'" + p.replace("'", "''") + "'" for p in parts)
    else:
        command = ' '.join(shlex.quote(p) for p in parts)
    rule = rendered_rule(config, command)
    rule = ('This workspace is a fictional demo. Use ONLY scope demo and its policy. '
            'Do not read any real work or personal vault for this demo.\n\n' + rule)
    for relative, content in {
        'codex/AGENTS.md': rule,
        'claude/CLAUDE.md': rule,
        'cursor/.cursor/rules/obsidian-knowledge.mdc':
            '---\ndescription: Fictional Obsidian demo\nalwaysApply: true\n---\n\n' + rule,
        'cursor/.cursor/mcp.json': '{"mcpServers": {}}\n',
        '.gitignore': '*\n',
    }.items():
        path = dest / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
    (dest / MARKER).write_text(json.dumps({'version': 1, 'note': NOTE}) + '\n', encoding='utf-8')
    print('Created fictional demo: ' + str(dest))
    print('Open vault/ in Obsidian; open codex/, claude/, or cursor/ in that AI client.')
    print('Start with Welcome.md or Welcome.ja.md in the vault. Created by UPHASH: https://uphash.net/')
    print('Global AI settings were not changed. Normal client authentication and workspace trust still apply.')
    print('Helper: ' + command)


def change_demo(dest):
    manifest = json.loads((dest / MARKER).read_text(encoding='utf-8'))
    if manifest != {'version': 1, 'note': NOTE}:
        raise ValueError('Not a supported generated demo')
    note = dest / 'vault' / NOTE
    before = note.read_bytes()
    if before.count(b'channel: blue') != 1 or before.count(b'channel is **blue**') != 1:
        raise ValueError('Demo was edited or already changed; create a fresh demo to repeat')
    after = before.replace(b'channel: blue', b'channel: teal').replace(b'channel is **blue**', b'channel is **teal**')
    stat = note.stat()
    note.write_bytes(after)
    os.utime(note, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    print('Changed demo channel blue -> teal; byte count and mtime preserved to test SHA-256 freshness.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
        epilog='Obsidian Agent Kit by UPHASH | MIT | https://uphash.net/')
    parser.add_argument('action', choices=['init', 'change'])
    parser.add_argument('--dest', type=Path, required=True)
    args = parser.parse_args(argv)
    dest = args.dest.expanduser().absolute()
    try:
        if args.action == 'init':
            init_demo(dest)
        else:
            change_demo(dest)
    except (OSError, ValueError) as exc:
        print('ERROR ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    sys.exit(main())
