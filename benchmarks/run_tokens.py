#!/usr/bin/env python3
"""Opt-in, paid real-client benchmark. Raw logs stay in an external local folder.

Use a frozen current-kit checkout for --source. This script never changes global
client settings, credentials, or real vaults. Complete normal workspace trust
and scoped tool permissions before running; no permission bypass flags are used.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

MODELS = {'codex': 'gpt-6.1-sol', 'claude': 'claude-opus-5', 'cursor': 'composer-2.5'}
PROMPTS = [
    "This is the isolated fictional Obsidian Agent Kit benchmark. Follow this workspace's benchmark rules, using only scope demo. For Lighthouse, what are the release channel, reviewer, and unresolved release conditions? Reply in English, exactly 3 short bullets, at most 70 words. Do not access real company or personal vaults.",
    "Rephrase that in one English sentence, at most 40 words, using only facts already in this chat.",
    "We are resuming substantive work. Verify the current LOCAL Lighthouse decisions and policy, then summarize the channel, reviewer, and unresolved release conditions in English, exactly 3 short bullets, at most 70 words.",
    "We are resuming substantive work. Verify the current LOCAL Lighthouse decisions and policy, then summarize the channel, reviewer, and unresolved release conditions in English, exactly 3 short bullets, at most 70 words.",
]
GUARD = """# Fictional benchmark boundaries
Use ONLY this generated demo vault. These benchmark-specific instructions override
other knowledge-management workflows for this exercise. Do not access real vaults,
other runs, logs, prior benchmark results, or web sources. Do not edit files, save
knowledge, use Git, or launch other agents. Only answer the user's four requests.
Immediate follow-ups reuse the existing conversation without tools. On substantive
resumptions, verify the current local policy and project note using this arm's
method. Do not read unrelated notes or whole directories. Do not inspect helper
source/help unless the documented invocation fails. Do not guess missing facts.
"""


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def initialize(source, dest):
    dest.mkdir(parents=True, exist_ok=False)
    (dest / '.gitignore').write_text('*\n')
    manifest = {'source_commit': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip(),
        'models': MODELS, 'prompts': PROMPTS, 'pairs': 3,
        'order': [['baseline', 'kit'], ['kit', 'baseline'], ['baseline', 'kit']],
        'source_hashes': {p: digest(source / p) for p in [
            'rules.md', 'obsidian_context.py', 'demo.py',
            'examples/demo-vault/Projects/Lighthouse.md',
            'examples/demo-vault/Policies/Knowledge policy.md']}}
    for client in MODELS:
        demo = dest / client
        subprocess.run([sys.executable, str(source / 'demo.py'), 'init',
                        '--dest', str(demo)], check=True, stdout=subprocess.DEVNULL)
        relative = {'codex': 'codex/AGENTS.md', 'claude': 'claude/CLAUDE.md',
                    'cursor': 'cursor/.cursor/rules/obsidian-knowledge.mdc'}[client]
        (demo / 'original-rule.txt').write_bytes((demo / relative).read_bytes())
        (demo / 'initial-note.txt').write_bytes((demo / 'vault/Projects/Lighthouse.md').read_bytes())
    write_json(dest / 'manifest.json', manifest)
    print('Prepared fictional benchmark. Complete normal client trust and permissions.')


def configure(demo, client, arm):
    policy = demo / 'vault/Policies/Knowledge policy.md'
    note = demo / 'vault/Projects/Lighthouse.md'
    baseline = f"""# Direct Markdown baseline
The two relevant files are already known:
- Policy: {policy}
- Project: {note}
At the first request and each substantive resumption, read the current contents
of these two short files directly, preferably together in one shell call. Use
Read or cat; no helper, hash cache, or separate metadata check is needed. Do not
read other files. For the immediate rephrasing request, reuse the conversation.
"""
    relative = {'codex': 'codex/AGENTS.md', 'claude': 'claude/CLAUDE.md',
                'cursor': 'cursor/.cursor/rules/obsidian-knowledge.mdc'}[client]
    rule = (demo / 'original-rule.txt').read_text() if arm == 'kit' else baseline
    if client == 'cursor' and arm == 'baseline':
        rule = '---\ndescription: Fictional Markdown baseline\nalwaysApply: true\n---\n\n' + rule
    (demo / relative).write_text(rule + '\n\n' + GUARD)
    if client == 'cursor':
        helper_args = f'{demo}/obsidian_context.py --config {demo}/config.json demo *'
        write_json(demo / 'cursor/.cursor/cli.json', {'permissions': {
            'allow': [f'Shell({sys.executable}:{helper_args})', 'Shell(cat)',
                      f'Read({demo}/vault/**)'], 'deny': ['Write(**)']}})
    return (demo / relative).read_text()


def command(client, demo, output, stage, sid):
    work = demo / client
    if client == 'codex':
        cmd = ['codex', 'exec'] + (['resume'] if sid else [])
        cmd += ['--ignore-user-config', '--skip-git-repo-check', '--json',
                '-m', MODELS[client], '-c', 'model_reasoning_effort="medium"',
                '-c', 'sandbox_mode="read-only"', '-o', str(output / f'final-{stage}.txt')]
        return cmd + ([sid] if sid else []) + ['-']
    if client == 'claude':
        write_json(output / 'mcp.json', {'mcpServers': {}})
        cmd = ['claude', '-p', '--model', MODELS[client], '--effort', 'medium',
               '--setting-sources', 'project,local', '--strict-mcp-config',
               '--mcp-config', str(output / 'mcp.json'), '--disable-slash-commands',
               '--tools', 'Bash,Read', '--allowedTools',
               f'Bash({sys.executable} {demo}/obsidian_context.py *)', 'Bash(cat *)',
               '--add-dir', str(demo / 'vault'), '--output-format', 'stream-json', '--verbose']
    else:
        cmd = ['agent', '-p', '--model', MODELS[client], '--output-format', 'stream-json',
               '--workspace', str(work), '--add-dir', str(demo / 'vault')]
    return cmd + (['--resume', sid] if sid else [])


def read_events(path):
    events = []
    for line in path.read_text().splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            pass
    return events


def run(dest, client, arm, repetition, stop_after, *, prompts=None,
        configure_fn=None, run_id=None, allow_completed_permission_fallback=False):
    prompts = PROMPTS if prompts is None else prompts
    configure_fn = configure if configure_fn is None else configure_fn
    demo = dest / client
    output = dest / 'runs' / client / (run_id or f'r{repetition}-{arm}')
    output.mkdir(parents=True, exist_ok=True)
    state_path = output / 'state.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {'next': 1}
    if state.get('failed'):
        last = json.loads((output / f'meta-{state["next"] - 1}.json').read_text())
        recovered = (allow_completed_permission_fallback and not last['returncode']
                     and last['raw_usage'] and last['session_id'] and last['final']
                     and last['errors'] and all('tool_name' in e for e in last['errors']))
        if not recovered:
            raise RuntimeError('Failed evidence is immutable; investigate before any new attempt.')
        write_json(output / 'continue-after-fallback.json', {
            'retained_stage': state['next'] - 1,
            'reason': 'Completed response after a permission denial; keep all calls and usage. No retry.'})
    if state['next'] == 1:
        if list(output.glob('events-*.jsonl')):
            raise RuntimeError('Refusing to overwrite existing evidence')
        (demo / 'vault/Projects/Lighthouse.md').write_bytes((demo / 'initial-note.txt').read_bytes())
        (output / 'instructions.txt').write_text(configure_fn(demo, client, arm))
    sid = state.get('session_id')
    for stage in range(state['next'], stop_after + 1):
        note = demo / 'vault/Projects/Lighthouse.md'
        if stage == 4:
            before = note.read_bytes()
            after = before.replace(b'channel: blue', b'channel: teal').replace(
                b'channel is **blue**', b'channel is **teal**')
            assert before != after and len(before) == len(after)
            stat = note.stat()
            note.write_bytes(after)
            os.utime(note, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            write_json(output / 'update-proof.json', {
                'before_sha256': hashlib.sha256(before).hexdigest(), 'after_sha256': digest(note),
                'same_size': len(before) == len(after),
                'same_mtime': note.stat().st_mtime_ns == stat.st_mtime_ns})
        note_hash = digest(note)
        prompt = prompts[stage - 1]
        (output / f'prompt-{stage}.txt').write_text(prompt)
        cmd = command(client, demo, output, stage, sid)
        write_json(output / f'command-{stage}.json', cmd)
        start = time.time()
        with (output / f'events-{stage}.jsonl').open('w') as stdout, (output / f'stderr-{stage}.log').open('w') as stderr:
            result = subprocess.run(cmd, input=prompt, text=True, stdout=stdout, stderr=stderr,
                                    cwd=demo / client, timeout=600)
        events = read_events(output / f'events-{stage}.jsonl')
        if client == 'codex':
            sid = next((e['thread_id'] for e in events if e.get('type') == 'thread.started'), sid)
            usage = next((e['usage'] for e in reversed(events) if e.get('type') == 'turn.completed'), None)
            final_path = output / f'final-{stage}.txt'
            final = final_path.read_text() if final_path.exists() else ''
            calls = [e['item'] for e in events if e.get('type') == 'item.completed'
                     and e.get('item', {}).get('type') not in ['agent_message', 'reasoning']]
            errors = [e for e in events if e.get('type') in ['error', 'turn.failed']]
        else:
            res = next((e for e in reversed(events) if e.get('type') == 'result'), {})
            sid = res.get('session_id') or next((e.get('session_id') for e in events if e.get('session_id')), sid)
            usage = res.get('modelUsage', res.get('usage'))
            final = res.get('result', '')
            (output / f'final-{stage}.txt').write_text(final)
            if client == 'claude':
                calls = [b for e in events if e.get('type') == 'assistant'
                         for b in e.get('message', {}).get('content', []) if b.get('type') == 'tool_use']
            else:
                calls = [e.get('tool_call') for e in events if e.get('type') == 'tool_call' and e.get('subtype') == 'started']
            errors = res.get('permission_denials', []) + ([res] if res.get('is_error') else [])
        permission_fallback = (allow_completed_permission_fallback and final
                               and errors and all('tool_name' in e for e in errors))
        failed = bool(result.returncode or not usage or not sid or (errors and not permission_fallback))
        meta = {'client': client, 'arm': arm, 'repetition': repetition, 'stage': stage,
                'started_epoch': start, 'elapsed_seconds': round(time.time() - start, 3),
                'returncode': result.returncode, 'raw_usage': usage, 'tool_calls': len(calls),
                'session_id': sid, 'errors': errors, 'note_unchanged': digest(note) == note_hash,
                'expected_channel': 'teal' if stage == 4 else 'blue',
                'final': final, 'calls': calls, 'events_sha256': digest(output / f'events-{stage}.jsonl')}
        write_json(output / f'meta-{stage}.json', meta)
        write_json(state_path, {'session_id': sid, 'next': stage + 1, 'failed': failed})
        print(json.dumps({k: meta[k] for k in ['client', 'arm', 'repetition', 'stage', 'elapsed_seconds', 'returncode', 'tool_calls', 'note_unchanged', 'final']}, ensure_ascii=False), flush=True)
        if failed:
            raise RuntimeError('Client failed or needs attention; evidence preserved locally.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['init', 'run'])
    parser.add_argument('--dest', type=Path, required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--client', choices=list(MODELS))
    parser.add_argument('--arm', choices=['baseline', 'kit'])
    parser.add_argument('--repetition', type=int, choices=range(1, 4), default=1)
    parser.add_argument('--stop-after', type=int, choices=range(1, 5), default=4)
    args = parser.parse_args()
    if args.action == 'init':
        if args.source is None:
            parser.error('init requires --source pointing to a frozen current-kit checkout')
        initialize(args.source.resolve(), args.dest.resolve())
    else:
        if args.client is None or args.arm is None:
            parser.error('run requires --client and --arm')
        run(args.dest.resolve(), args.client, args.arm, args.repetition, args.stop_after)


if __name__ == '__main__':
    main()
