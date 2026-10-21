#!/usr/bin/env python3
"""Export all direct/current-kit trials without machine paths or account IDs."""
import argparse
import csv
import json
from pathlib import Path
import re

try:
    from .aggregate_tokens import FIELDS, normalize, reduction, statuses
    from .aggregate_long_notes import action_summaries, quality, tool_outputs
    from .long_notes import SCENARIOS
    from .revision_tokens import ARMS
    from .run_tokens import read_events, write_json
except ImportError:
    from aggregate_tokens import FIELDS, normalize, reduction, statuses
    from aggregate_long_notes import action_summaries, quality, tool_outputs
    from long_notes import SCENARIOS
    from revision_tokens import ARMS
    from run_tokens import read_events, write_json


def freshness_checks(rows, scenario):
    """Check evidence from actual tool results, separately from correct answers."""
    names = ['Lighthouse'] if scenario == 'single-full' else ['Lighthouse', 'Orchard', 'Atlas']
    paths = {'Policies/Knowledge policy.md', *[f'Projects/{n}.md' for n in names]}
    by_stage = {r['stage']: {s['path']: s for s in r['helper_statuses']} for r in rows}
    initial, unchanged, changed = (by_stage[s] for s in [1, 3, 4])
    changed_path = 'Projects/Lighthouse.md'
    present = all(set(d) == paths for d in [initial, unchanged, changed])
    return {
        'immediate_zero_calls': rows[1]['tool_calls'] == 0,
        'all_required_hashes_present': present,
        'initial_all_content': present and all(s['status'] == 'CONTENT' for s in initial.values()),
        'unchanged_all_unchanged': present and all(
            unchanged[p]['status'] == 'UNCHANGED' and unchanged[p]['sha256'] == initial[p]['sha256']
            for p in paths),
        'changed_note_only_content': present and all(
            changed[p]['status'] == ('CONTENT' if p == changed_path else 'UNCHANGED')
            and ((changed[p]['sha256'] != initial[p]['sha256']) if p == changed_path
                 else (changed[p]['sha256'] == initial[p]['sha256'])) for p in paths),
    }


def comparison(client, runs, rows):
    selected = [r for r in runs if r['client'] == client]
    totals = {a: {k: sum(r[k] for r in selected if r['arm'] == a)
                  for k in FIELDS + ['total', 'tool_calls', 'tool_output_bytes']}
              for a in ARMS}
    result = {'client': client, 'totals': totals,
              'all_answers_correct': all(r['all_answers_correct'] for r in selected)}
    for before in ['baseline']:
        before_runs = sorted((r for r in selected if r['arm'] == before), key=lambda r: r['repetition'])
        after_runs = sorted((r for r in selected if r['arm'] == 'improved'), key=lambda r: r['repetition'])
        result[before + '_to_improved'] = {
            'reduction_percent': reduction(totals[before]['total'], totals['improved']['total']),
            'paired_reduction_percent': [reduction(b['total'], a['total']) for b, a in zip(before_runs, after_runs)],
            'tool_output_byte_reduction_percent': reduction(
                totals[before]['tool_output_bytes'], totals['improved']['tool_output_bytes'])}
    result['stages'] = []
    for stage in range(1, 5):
        values = {a: sum(r['total'] for r in rows if r['client'] == client and r['arm'] == a
                        and r['stage'] == stage) for a in ARMS}
        result['stages'].append({'stage': stage, **values,
                                **{a + '_reduction_percent': reduction(values[a], values['improved'])
                                   for a in ['baseline']}})
    return result


def annotated_actions(client, calls):
    actions = action_summaries(client, calls)
    for action, call in zip(actions, calls):
        if not action['mode'].startswith('helper-'):
            continue
        if client == 'codex':
            command = call.get('command', '')
        elif client == 'claude':
            command = call.get('input', {}).get('command', '')
        else:
            command = call.get('shellToolCall', {}).get('args', {}).get('command', '')
        action['compact'] = '--compact' in command
        action['explicit_section'] = '--section' in command
        action['both_required_headings_named'] = all(h in command for h in ['Current decisions', 'Release gates'])
    return actions


def aggregate(source, output):
    manifest = json.loads((source / 'manifest.json').read_text())
    overview = []
    for scenario in SCENARIOS:
        rows, runs = [], []
        for client in manifest['models']:
            for repetition in [1, 2]:
                for arm in ARMS:
                    root = source / 'runs' / client / f'{scenario}-r{repetition}-{arm}'
                    previous, run_rows = None, []
                    for stage in range(1, 5):
                        meta = json.loads((root / f'meta-{stage}.json').read_text())
                        if (any('tool_name' not in e for e in meta['errors'])
                                or meta['returncode'] or not meta['note_unchanged']):
                            raise ValueError('Incomplete/failed evidence: ' + root.name)
                        counters = normalize(client, meta['raw_usage'], previous)
                        previous = meta['raw_usage']
                        events = read_events(root / f'events-{stage}.jsonl')
                        bodies = list(tool_outputs(client, events))
                        row = {k: meta[k] for k in ['client', 'arm', 'repetition', 'stage',
                               'tool_calls', 'elapsed_seconds', 'events_sha256']}
                        row.update(counters, answer=meta['final'],
                                   quality=quality(meta['final'], scenario, stage),
                                   helper_statuses=statuses(bodies),
                                   tool_actions=annotated_actions(client, meta['calls']),
                                   permission_denials=len(meta['errors']),
                                   tool_output_bytes=sum(len(t.encode('utf-8')) for t in bodies))
                        rows.append(row)
                        run_rows.append(row)
                    proof = json.loads((root / 'update-proof.json').read_text())
                    if not proof['same_size'] or not proof['same_mtime'] or proof['before_sha256'] == proof['after_sha256']:
                        raise ValueError('Invalid same-metadata mutation')
                    checks = freshness_checks(run_rows, scenario) if arm != 'baseline' else None
                    if checks is not None:
                        expected_hashes = {f'Projects/{n}': v['sha256'] for n, v in manifest['fixture'].items()}
                        expected_hashes['Policies/Knowledge policy.md'] = manifest['source_hashes'][
                            'examples/demo-vault/Policies/Knowledge policy.md']
                        checks['hashes_match_fixture'] = all(
                            s['sha256'] == (proof['after_sha256'] if row['stage'] == 4
                            and s['path'] == 'Projects/Lighthouse.md' else expected_hashes.get(s['path']))
                            for row in run_rows for s in row['helper_statuses'])
                    runs.append({'client': client, 'arm': arm, 'repetition': repetition,
                        **{k: sum(r[k] for r in run_rows) for k in FIELDS + ['total', 'tool_calls', 'tool_output_bytes']},
                        'all_answers_correct': all(r['quality']['exact_facts'] for r in run_rows),
                        'strict_format_passes': sum(r['quality']['exact_facts_and_format'] for r in run_rows),
                        'permission_denials': sum(r['permission_denials'] for r in run_rows),
                        'immediate_zero_calls': run_rows[1]['tool_calls'] == 0,
                        'helper_checks': checks,
                        'same_metadata_update': proof})
        comparisons = [comparison(c, runs, rows) for c in manifest['models']]
        overview.extend({'scenario': scenario, **c} for c in comparisons)
        result = {'date': manifest['date'], 'scenario': scenario,
                  'definition': manifest['scenarios'][scenario], 'versions': manifest['versions'],
                  'fixture': manifest['fixture'], 'models': manifest['models'],
                  'client_versions': manifest['client_versions'], 'order': manifest['order'][scenario],
                  'prompts': manifest['prompts'][scenario], 'rendered_rule_bytes': manifest['rendered_rule_bytes'],
                  'metric': 'Client-reported input including cache plus output; not money or quota',
                  'tool_output_metric': 'UTF-8 tool body bytes; not model tokens; excludes event wrappers',
                  'comparisons': comparisons, 'runs': runs, 'turns': rows}
        encoded = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        if re.search(r'/(?:Users|home)/[^/]+/|[A-Za-z]:[\\/]Users[\\/]', encoded):
            raise ValueError('Local user path in export')
        if len(encoded.encode()) > 200_000:
            raise ValueError('Split the public export before publication')
        target = output / scenario
        target.mkdir(parents=True, exist_ok=True)
        (target / 'results.json').write_text(encoded)
        columns = ['client', 'arm', 'repetition', 'stage'] + FIELDS + ['total', 'tool_calls', 'tool_output_bytes', 'elapsed_seconds']
        with (target / 'per-turn.csv').open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(rows)
    write_json(output / 'summary.json', overview)
    print(json.dumps([{'scenario': r['scenario'], 'client': r['client'],
                      'baseline_to_improved': r['baseline_to_improved']['reduction_percent'],
                      'all_answers_correct': r['all_answers_correct']} for r in overview], indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    aggregate(args.source.resolve(), args.output.resolve())
