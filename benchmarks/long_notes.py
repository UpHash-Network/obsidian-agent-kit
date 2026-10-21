#!/usr/bin/env python3
"""Deterministic fictional workload; optional real-client runs incur model usage.

Reusable fixture generation, prompts and direct-read instructions for the
current-kit runner. Initialization never invokes a model.
"""
import argparse
from functools import partial
import json
from pathlib import Path
import shlex
import subprocess
import sys

try:
    from . import run_tokens as base
except ImportError:
    import run_tokens as base

PROJECTS = ['Lighthouse', 'Orchard', 'Atlas', 'Cedar', 'Harbor', 'Meadow',
            'Quartz', 'Summit', 'Willow', 'Comet', 'Juniper', 'Maple']
CHANNELS = ['blue', 'gold', 'rose', 'jade']
REVIEWERS = ['Mira', 'Kian', 'Nora', 'Ezra']
BLOCKERS = ['security sign-off', 'accessibility review', 'restore test', 'capacity review']
SCENARIOS = {
    'single-full': {'projects': PROJECTS[:1], 'baseline': 'full'},
    'multi-full': {'projects': PROJECTS[:3], 'baseline': 'full'},
    'multi-focused': {'projects': PROJECTS[:3], 'baseline': 'focused'},
}
RELATIVE = {'codex': 'codex/AGENTS.md', 'claude': 'claude/CLAUDE.md',
            'cursor': 'cursor/.cursor/rules/obsidian-knowledge.mdc'}


def note(name, index):
    """A project brief, historical work records, and a current gate at the end."""
    parts = [f'''---
scope: demo
asset_type: project
status: confirmed
project: {name.lower()}
date: 2026-02-28
channel: {CHANNELS[index % 4]}
---
# {name}

## Current decisions
The current release channel is **{CHANNELS[index % 4]}**.
The current release reviewer is **{REVIEWERS[index % 4]}**.
These are the confirmed current choices for this project only. Historical
records below explain earlier experiments and do not override current choices.
The current unresolved blocker is documented in the final **Release gates**
section. Read that section before describing readiness. A channel assignment
does not constitute release approval. This is a fictional internal dashboard
for planning service deployments; no real organization or customer is involved.

## Historical delivery records
Everything in this section is archived context, not current release authority.
''']
    components = ['import queue', 'review dashboard', 'notification worker',
                  'export service', 'audit timeline', 'search index',
                  'accessibility panel', 'retry controller', 'backup catalog']
    issues = ['duplicate event handling', 'slow query pagination', 'missing timezone labels',
              'incomplete keyboard focus', 'retry backoff drift', 'stale permission hints']
    actions = ['added a bounded retry window', 'documented the rollback procedure',
               'split the operator checklist', 'introduced a deterministic test fixture',
               'measured the empty-state rendering path', 'reviewed the failure message wording']
    for n in range(36):
        component = components[(n + index) % len(components)]
        issue = issues[(n * 5 + index) % len(issues)]
        action = actions[(n * 7 + index) % len(actions)]
        parts.append(f'''
### Archived work item {name[:3].upper()}-{100 + n}
The {component} trial examined {issue}. The team {action}.
The synthetic test used {120 + 7*n + index} records across {2 + n%5} simulated tenants,
with a {15 + n%13} minute observation window. Operators recorded the outcome in
the weekly handover and kept the previous implementation available for rollback.
An early proposal used the silver channel with reviewer Theo; that proposal was
superseded. It is historical context and must not replace Current decisions.
Next checks covered recovery behavior, display labels, and whether a failed
request could be replayed without duplicating work. This entry gives historical
implementation context; it makes no current approval or release-date claim.
''')
    parts.append(f'''
## Release gates
The current unresolved release blocker is **{BLOCKERS[index % 4]}**.
It remains pending; there is no recorded approval or confirmed release date.
Report the blocker as pending, rather than treating archived test completion as
approval. Gate status applies only to {name}, not to neighboring project notes.

Source: wholly fictional deterministic benchmark fixture, authored for this test.
''')
    return ''.join(parts)


def expected(scenario, stage):
    return {'projects': [dict(project=p,
                channel='teal' if p == 'Lighthouse' and stage == 4 else CHANNELS[PROJECTS.index(p) % 4],
                reviewer=REVIEWERS[PROJECTS.index(p) % 4],
                blocker=BLOCKERS[PROJECTS.index(p) % 4])
            for p in SCENARIOS[scenario]['projects']], 'automatic_git_sync': False}


def prompts(scenario):
    names = ', '.join(SCENARIOS[scenario]['projects'])
    question = (f'For {names}, report the current release channel, reviewer, and unresolved release blocker. '
                'Also report whether this demo automatically synchronizes Git. Return only compact JSON, '
                'without a code fence, with keys projects (an array of objects with keys project, channel, '
                'reviewer, blocker) and automatic_git_sync (boolean). Use project order as requested, '
                'exact values from the source, and no extra keys. Do not guess missing facts.')
    return ["This is the isolated fictional long-note benchmark. Follow the workspace rules. " + question,
            "Repeat the same compact JSON using only the facts already in this conversation; no tools.",
            "We are resuming substantive work. Verify the current LOCAL policy and relevant project notes. " + question,
            "We are resuming substantive work. Verify the current LOCAL policy and relevant project notes. " + question]


def initialize(source, dest):
    base.initialize(source, dest)
    fixture = dest / 'fixture'
    fixture.mkdir()
    for i, name in enumerate(PROJECTS):
        (fixture / f'{name}.md').write_text(note(name, i), encoding='utf-8')
    for client in base.MODELS:
        demo = dest / client
        projects = demo / 'vault/Projects'
        for p in projects.glob('*.md'):
            p.unlink()  # Only the newly generated demo's two original sample notes.
        for p in fixture.glob('*.md'):
            (projects / p.name).write_bytes(p.read_bytes())
        (demo / 'initial-note.txt').write_bytes((projects / 'Lighthouse.md').read_bytes())
    manifest = json.loads((dest / 'manifest.json').read_text())
    manifest.update(pairs=2, order=[['baseline', 'kit'], ['kit', 'baseline']],
                    scenarios=SCENARIOS, prompts={s: prompts(s) for s in SCENARIOS},
                    client_versions={c: subprocess.check_output([c, '--version'], text=True).strip()
                                     for c in ['codex', 'claude', 'agent']},
                    fixture={p.name: {'bytes': p.stat().st_size, 'sha256': base.digest(p)}
                             for p in sorted(fixture.glob('*.md'))})
    base.write_json(dest / 'manifest.json', manifest)
    print(json.dumps(manifest['fixture'], indent=2))


def configure(demo, client, arm, scenario):
    spec = SCENARIOS[scenario]
    paths = ['Policies/Knowledge policy.md'] + [f'Projects/{p}.md' for p in spec['projects']]
    common = '''# Fictional long-note benchmark boundaries
Use ONLY the generated demo vault. Override any other knowledge-management
workflow for this exercise. Do not read other runs, logs, source code, real
vaults, web pages or prior benchmark results. Do not edit, save, use Git or
launch agents. Immediate follow-ups use zero tools. Substantive resumptions
verify the LOCAL policy and relevant notes. Do not read unrelated projects.
If output is truncated or required sections are missing, retrieve the missing
evidence before answering. Never guess. Historical records are not current.
'''
    common += '\nThe relevant files are already known (no discovery benchmark):\n'
    common += ''.join(f'- {p}\n' for p in paths)
    common += ('\nCurrent facts are in each project’s `Current decisions` and final `Release gates` '
               'sections, plus the policy. Both sections are necessary. Archive details are irrelevant '
               'to this question. Multiple projects in this request are explicitly in scope.\n')
    if arm == 'kit':
        rule = (demo / 'original-rule.txt').read_text()
    else:
        rule = '# Direct Markdown baseline\n'
        rule += f'Vault: {demo / "vault"}\n'
        if spec['baseline'] == 'full':
            rule += ('At first request and each substantive resumption read the full current policy and '
                     'only the specified project notes directly, preferably one batched cat call. '
                     'Use a sufficient output budget or recover truncated output. '
                     'This arm measures the common full-note reading workflow.\n')
        else:
            # A normal shell excerpt, not a persistent cache or a second custom helper.
            awk = '/^## / {keep=($0=="## Current decisions" || $0=="## Release gates")} keep {print}'
            full = [str(demo / 'vault' / p) for p in paths]
            example = 'cat ' + shlex.quote(full[0]) + '; awk ' + shlex.quote(awk)
            example += ' ' + ' '.join(shlex.quote(p) for p in full[1:])
            rule += ('At first request and each substantive resumption read the policy and only the '
                     'Current decisions and Release gates sections of the specified project notes. '
                     'Use one batched shell call with cat and awk, or equivalent focused Read calls. '
                     'Do not reread historical records. An exact optional command is:\n' + example + '\n')
        rule += ('No helper, hash cache or separate metadata check. For immediate follow-ups reuse '
                 'the conversation. Freshness on resumption comes from rereading current contents.\n')
        if client == 'cursor':
            rule = '---\ndescription: Fictional long-note baseline\nalwaysApply: true\n---\n\n' + rule
    (demo / RELATIVE[client]).write_text(rule + '\n' + common)
    if client == 'cursor':
        helper = f'{demo}/obsidian_context.py --config {demo}/config.json demo *'
        base.write_json(demo / 'cursor/.cursor/cli.json', {'permissions': {
            'allow': [f'Shell({sys.executable}:{helper})', 'Shell(cat)', 'Shell(awk)',
                      f'Read({demo}/vault/**)'], 'deny': ['Write(**)']}})
    # Project-local allow rules for Claude; no global configuration edits.
    if client == 'claude':
        base.write_json(demo / 'claude/.claude/settings.local.json', {
            'permissions': {'allow': ['Bash(awk *)']}})
    return (demo / RELATIVE[client]).read_text()


def run(dest, client, scenario, repetition, arm, stop_after):
    vault = dest / client / 'vault'
    static = {p: base.digest(p) for p in vault.rglob('*.md') if p.name != 'Lighthouse.md'}
    base.run(dest, client, arm, repetition, stop_after, prompts=prompts(scenario),
             configure_fn=partial(configure, scenario=scenario),
             run_id=f'{scenario}-r{repetition}-{arm}', allow_completed_permission_fallback=True)
    if any(base.digest(p) != h for p, h in static.items()):
        raise RuntimeError('An unrelated fixture note changed; inspect evidence.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['init', 'run'])
    parser.add_argument('--dest', type=Path, required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--client', choices=list(base.MODELS))
    parser.add_argument('--scenario', choices=list(SCENARIOS))
    parser.add_argument('--repetition', type=int, choices=[1, 2], default=1)
    parser.add_argument('--arm', choices=['baseline', 'kit'])
    parser.add_argument('--stop-after', type=int, choices=range(1, 5), default=4)
    args = parser.parse_args()
    if args.action == 'init':
        if not args.source:
            parser.error('init requires --source (frozen current-kit checkout)')
        initialize(args.source.resolve(), args.dest.resolve())
    else:
        if not all([args.client, args.scenario, args.arm]):
            parser.error('run requires --client, --scenario, and --arm')
        run(args.dest.resolve(), args.client, args.scenario, args.repetition, args.arm, args.stop_after)


if __name__ == '__main__':
    main()
