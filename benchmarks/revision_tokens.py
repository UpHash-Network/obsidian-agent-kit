#!/usr/bin/env python3
"""Compare direct reading with the current kit on deterministic long notes.

Opt in only: these real authenticated CLI runs consume model usage. Raw logs and
rendered paths stay outside the repository. No global AI settings are changed.
"""
import argparse
from datetime import date
from functools import partial
import json
from pathlib import Path
import runpy
import shlex
import shutil
import subprocess
import sys

try:
    from . import long_notes as workload
    from . import run_tokens as base
except ImportError:
    import long_notes as workload
    import run_tokens as base

ARMS = ['baseline', 'improved']
ORDERS = [
    [['baseline', 'improved'], ['improved', 'baseline']],
    [['improved', 'baseline'], ['baseline', 'improved']],
    [['improved', 'baseline'], ['baseline', 'improved']],
]
PREFIX = ('This workspace is a fictional demo. Use ONLY scope demo and its policy. '
          'Do not read any real work or personal vault for this demo.\n\n')
CURSOR_PREFIX = '---\ndescription: Fictional Obsidian demo\nalwaysApply: true\n---\n\n'


def initialize(improved, dest):
    sys.path.insert(0, str(improved))
    try:
        render = runpy.run_path(str(improved / 'setup.py'))['rendered_rule']
    finally:
        sys.path.pop(0)
    workload.initialize(improved, dest)
    versions = {}
    for arm, source in [('improved', improved)]:
        target = dest / 'versions' / arm
        target.mkdir(parents=True)
        shutil.copyfile(source / 'obsidian_context.py', target / 'obsidian_context.py')
        versions[arm] = {
            'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip(),
            'hashes': {p: base.digest(source / p) for p in ['obsidian_context.py', 'rules.md', 'setup.py']}}
    for client in base.MODELS:
        demo = dest / client
        config = json.loads((demo / 'config.json').read_text())
        parts = [sys.executable, str(demo / 'obsidian_context.py'), '--config', str(demo / 'config.json')]
        command = ' '.join(shlex.quote(p) for p in parts)
        rule = PREFIX + render(config, command)
        if client == 'cursor':
            rule = CURSOR_PREFIX + rule
        (demo / 'improved-rule.txt').write_text(rule)
    manifest = json.loads((dest / 'manifest.json').read_text())
    manifest.update(date=date.today().isoformat(), versions=versions, arms=ARMS,
                    order={s: ORDERS[i] for i, s in enumerate(workload.SCENARIOS)})
    manifest['rendered_rule_bytes'] = {c: {a: (dest / c / f'{a}-rule.txt').stat().st_size
                                         for a in ['improved']} for c in base.MODELS}
    base.write_json(dest / 'manifest.json', manifest)
    print(json.dumps({'versions': versions, 'rendered_rule_bytes': manifest['rendered_rule_bytes']}, indent=2))


def configure(demo, client, arm, scenario):
    version = 'improved'
    shutil.copyfile(demo.parent / 'versions' / version / 'obsidian_context.py', demo / 'obsidian_context.py')
    shutil.copyfile(demo / f'{version}-rule.txt', demo / 'original-rule.txt')
    return workload.configure(demo, client, 'baseline' if arm == 'baseline' else 'kit', scenario)


def run(dest, client, scenario, repetition, arm):
    vault = dest / client / 'vault'
    static = {p: base.digest(p) for p in vault.rglob('*.md') if p.name != 'Lighthouse.md'}
    base.run(dest, client, arm, repetition, 4, prompts=workload.prompts(scenario),
             configure_fn=partial(configure, scenario=scenario),
             run_id=f'{scenario}-r{repetition}-{arm}', allow_completed_permission_fallback=True)
    if any(base.digest(p) != h for p, h in static.items()):
        raise RuntimeError('Unrelated fixture changed; inspect evidence')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['init', 'run-client'])
    parser.add_argument('--dest', type=Path, required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--client', choices=list(base.MODELS))
    args = parser.parse_args()
    if args.action == 'init':
        if not args.source:
            parser.error('init requires --source pointing to a frozen kit checkout')
        initialize(args.source.resolve(), args.dest.resolve())
    else:
        if not args.client:
            parser.error('run-client requires --client')
        for i, scenario in enumerate(workload.SCENARIOS):
            for repetition, arms in enumerate(ORDERS[i], 1):
                for arm in arms:
                    print('START', args.client, scenario, repetition, arm, flush=True)
                    run(args.dest.resolve(), args.client, scenario, repetition, arm)


if __name__ == '__main__':
    main()
