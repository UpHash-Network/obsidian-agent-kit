#!/usr/bin/env python3
# Copyright (c) 2026 UPHASH Inc. SPDX-License-Identifier: MIT
"""Install the local helper and managed AI instructions; never sync vaults."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile

from obsidian_context import VERSION, confined, load_config

SOURCE = Path(__file__).resolve().parent
BEGIN = '<!-- obsidian-context:begin -->'
END = '<!-- obsidian-context:end -->'
LEGACY = '## Obsidian: focused knowledge, one conditional call'


def save(path, content, backup_root, executable=False):
    """Write atomically; retain the exact previous bytes before each changed file."""
    raw = content.encode('utf-8') if isinstance(content, str) else content
    if path.exists() and path.read_bytes() == raw:
        return False
    if path.is_symlink():
        raise ValueError('Refusing to replace a symlink: ' + str(path))
    if path.exists():
        backup_root.mkdir(parents=True, exist_ok=True)
        old = path.read_bytes()
        key = hashlib.sha256(str(path).encode()).hexdigest()[:12]
        tag = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        backup = backup_root / (path.name + '.' + key + '.' + tag + '.bak')
        backup.write_bytes(old)
        backup.chmod(0o600)
        print('BACKUP ' + str(path) + ' -> ' + str(backup))
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(raw)
        os.chmod(name, 0o700 if executable else 0o600)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    print('UPDATED ' + str(path))
    return True


def merge_rule(old, body, migrate=False):
    block = BEGIN + '\n' + body.rstrip() + '\n' + END
    if BEGIN in old or END in old:
        if old.count(BEGIN) != 1 or old.count(END) != 1 or old.index(BEGIN) > old.index(END):
            raise ValueError('Malformed managed rule markers; repair them before installation')
        a, b = old.index(BEGIN), old.index(END) + len(END)
        return old[:a] + block + old[b:]
    if LEGACY in old:
        if not migrate or old.count(LEGACY) != 1:
            raise ValueError('Existing legacy Obsidian section: review it, then use --migrate-legacy')
        a = old.index(LEGACY)
        next_heading = re.search(r'^## ', old[a + len(LEGACY):], flags=re.M)
        b = a + len(LEGACY) + next_heading.start() if next_heading else len(old)
        return old[:a] + block + '\n\n' + old[b:]
    return old + ('\n\n' if old and not old.endswith('\n\n') else '') + block + '\n'


def installed_paths(home):
    base = home / '.local/share/obsidian-context'
    launcher = home / '.local/bin' / ('obsidian-context.cmd' if os.name == 'nt' else 'obsidian-context')
    return base, launcher


def command_for(helper, launcher, config):
    if os.name == 'nt':
        quote = lambda s: "'" + str(s).replace("'", "''") + "'"
        return '& ' + ' '.join(quote(x) for x in (sys.executable, helper, '--config', config))
    return shlex.quote(str(launcher))


def rendered_rule(config, command):
    lines = []
    for scope, spec in config['scopes'].items():
        owner = ', '.join(spec.get('owners', [])) or scope
        lines.append(f"- {owner}: scope `{scope}`, vault `{spec['root']}`, policy `{spec['policy']}`, sync `{spec['sync']}`.")
    scope = 'personal' if 'personal' in config['scopes'] else next(iter(config['scopes']))
    body = (SOURCE / 'rules.md').read_text(encoding='utf-8')
    for key, value in {'scopes': '\n'.join(lines), 'command': command, 'scope': scope,
                       'policy': config['scopes'][scope]['policy']}.items():
        body = body.replace('{{' + key + '}}', value)
    return body


def instruction_paths(home, codex_home, claude_home):
    return [codex_home / 'AGENTS.md', claude_home / 'CLAUDE.md',
            home / '.cursor/rules/obsidian-knowledge.mdc']


def install(args):
    config = load_config(args.config)
    base, launcher = installed_paths(args.home)
    helper = base / 'obsidian_context.py'
    command = command_for(helper, launcher, args.config)
    body = rendered_rule(config, command)
    # Validate every merge before changing any existing instruction file.
    updates = []
    for path in instruction_paths(args.home, args.codex_home, args.claude_home):
        old = path.read_text(encoding='utf-8') if path.exists() else ''
        if path.suffix == '.mdc' and not old:
            old = '---\ndescription: Scoped Obsidian knowledge\nalwaysApply: true\n---\n\n'
        updates.append((path, merge_rule(old, body, args.migrate_legacy)))
    if os.name == 'nt':
        # cmd wrappers cannot faithfully represent percent signs in expanded paths.
        parts = (sys.executable, str(helper), str(args.config))
        if any('%' in p or '\n' in p or '\r' in p for p in parts):
            raise ValueError('Windows install paths must not contain percent signs or line breaks')
        wrapper = '@echo off\r\n"' + parts[0] + '" "' + parts[1] + '" --config "' + parts[2] + '" %*\r\n'
    else:
        wrapper = '#!/bin/sh\nexec ' + ' '.join(shlex.quote(str(x)) for x in
                   (sys.executable, helper, '--config', args.config)) + ' "$@"\n'
    backup = base / 'backups'
    save(helper, (SOURCE / 'obsidian_context.py').read_bytes(), backup)
    save(base / 'LICENSE', (SOURCE / 'LICENSE').read_bytes(), backup)
    save(launcher, wrapper, backup, executable=True)
    for path, text in updates:
        save(path, text, backup)
    save(base / 'cursor-user-rule.txt', body, backup)
    print('VERSION ' + VERSION)
    print('COMMAND ' + command)
    print('CURSOR MANUAL: paste ' + str(base / 'cursor-user-rule.txt') +
          ' into Customize > Rules > User Rules (replace the previous Obsidian rule).')
    print('The .cursor/rules file above is a compatibility reference, not an automatically loaded global Cursor rule.')
    print('Restart AI sessions after applying rules. Vault contents and sync settings were not changed.')
    return 0


def configure(args):
    data = load_config(args.config) if args.config.exists() else {'version': 1, 'scopes': {}}
    scope = args.scope
    spec = {'root': str(args.vault.expanduser().resolve()),
            'policy': args.policy or 'Policies/Knowledge policy.md',
            'sync': 'local' if scope == 'personal' or args.local_only else 'git',
            'owners': args.owner or []}
    data['scopes'][scope] = spec
    # Validate in a temporary file before replacing a working configuration.
    raw = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    with tempfile.TemporaryDirectory() as temp:
        candidate = Path(temp) / 'config.json'
        candidate.write_text(raw, encoding='utf-8')
        load_config(candidate)
    save(args.config, raw, installed_paths(args.home)[0] / 'backups')
    print('Run install after configuring all scopes. Existing notes are never created or overwritten.')
    return 0


def doctor(args):
    config = load_config(args.config)
    base, launcher = installed_paths(args.home)
    helper = base / 'obsidian_context.py'
    failures = 0
    expected = rendered_rule(config, command_for(helper, launcher, args.config)).strip()
    for path in instruction_paths(args.home, args.codex_home, args.claude_home):
        text = path.read_text(encoding='utf-8') if path.exists() else ''
        ok = BEGIN in text and END in text and expected in text
        print(('OK ' if ok else 'ERROR ') + str(path))
        failures += not ok
    for scope, spec in config['scopes'].items():
        try:
            policy = confined(Path(spec['root']).expanduser(), spec['policy'])
            result = subprocess.run([sys.executable, str(helper), '--config', str(args.config),
                                     scope, '--file', spec['policy'], '--chars', '100'],
                                    capture_output=True, text=True, encoding='utf-8', timeout=15)
            if result.returncode:
                errors = [json.loads(line).get('error', '') for line in result.stdout.splitlines()
                          if line.startswith('{') and json.loads(line).get('status') == 'ERROR']
                raise ValueError(result.stderr.strip() or '; '.join(errors) or 'Installed helper could not read the policy')
            print('OK scope ' + scope + ' policy ' + str(policy))
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            print('ERROR scope ' + scope + ': ' + str(exc))
            failures += 1
    if not launcher.is_file() or not helper.is_file() or helper.read_bytes() != (SOURCE / 'obsidian_context.py').read_bytes():
        print('ERROR installed helper/launcher missing or helper differs from this checkout; run install')
        failures += 1
    print('MANUAL Cursor User Rules activation and each AI conversation must be verified in the app.')
    print('MANUAL Git pull/push freshness and permissions are outside this read-only doctor.')
    print('PASS local checks' if not failures else 'FAIL local checks: ' + str(failures))
    return 1 if failures else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
        epilog='Obsidian Agent Kit by UPHASH | MIT | https://uphash.net/')
    ap.add_argument('action', choices=['configure', 'install', 'doctor'])
    ap.add_argument('--home', type=Path, default=Path.home(), help='Target home; mainly for isolated tests')
    ap.add_argument('--config', type=Path, help='Default: OBSIDIAN_CONTEXT_CONFIG or ~/.config/obsidian-context/config.json')
    ap.add_argument('--codex-home', type=Path, help='Override CODEX_HOME/default ~/.codex')
    ap.add_argument('--claude-home', type=Path, help='Override CLAUDE_CONFIG_DIR/default ~/.claude')
    ap.add_argument('--scope')
    ap.add_argument('--vault', type=Path)
    ap.add_argument('--policy')
    ap.add_argument('--owner', action='append')
    ap.add_argument('--local-only', action='store_true')
    ap.add_argument('--migrate-legacy', action='store_true', help='Replace the known legacy Obsidian section; keep other sections')
    args = ap.parse_args(argv)
    args.home = args.home.expanduser().resolve()
    args.config = (args.config or Path(os.environ.get('OBSIDIAN_CONTEXT_CONFIG',
                   str(args.home / '.config/obsidian-context/config.json')))).expanduser().resolve()
    args.codex_home = (args.codex_home or Path(os.environ.get('CODEX_HOME', str(args.home / '.codex')))).expanduser().resolve()
    args.claude_home = (args.claude_home or Path(os.environ.get('CLAUDE_CONFIG_DIR', str(args.home / '.claude')))).expanduser().resolve()
    if args.action == 'configure' and (not args.scope or not args.vault):
        ap.error('configure requires --scope and --vault')
    try:
        return {'configure': configure, 'install': install, 'doctor': doctor}[args.action](args)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('ERROR ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    sys.exit(main())
