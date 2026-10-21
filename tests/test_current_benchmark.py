"""Check public evidence integrity and the current two-method fixture setup."""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from benchmarks.aggregate_revision import comparison, freshness_checks
from benchmarks.aggregate_tokens import FIELDS
from benchmarks.long_notes import PROJECTS, SCENARIOS, note
from benchmarks.revision_tokens import ARMS, configure, initialize

SOURCE = Path(__file__).resolve().parents[1]


class CurrentBenchmarkTests(unittest.TestCase):
    def test_published_counters_answers_and_freshness_remain_consistent(self):
        summary = []
        total_turns = 0
        for scenario in SCENARIOS:
            data = json.loads((SOURCE / 'benchmarks/v0.1.2' / scenario / 'results.json').read_text(encoding='utf-8'))
            self.assertEqual(len(data['runs']), 12)
            self.assertEqual(len(data['turns']), 48)
            self.assertEqual({r['arm'] for r in data['runs']}, set(ARMS))
            for name, digest in data['versions']['improved']['hashes'].items():
                self.assertEqual(hashlib.sha256((SOURCE / name).read_bytes()).hexdigest(), digest)
            for index, name in enumerate(PROJECTS):
                self.assertEqual(hashlib.sha256(note(name, index).encode()).hexdigest(),
                                 data['fixture'][name + '.md']['sha256'])
            for run in data['runs']:
                turns = [t for t in data['turns'] if all(t[k] == run[k]
                         for k in ['client', 'arm', 'repetition'])]
                self.assertEqual([t['stage'] for t in turns], [1, 2, 3, 4])
                for field in FIELDS + ['total', 'tool_calls', 'tool_output_bytes']:
                    self.assertEqual(run[field], sum(t[field] for t in turns))
                for turn in turns:
                    self.assertEqual(turn['total'], sum(turn[k] for k in FIELDS))
                if run['arm'] == 'improved':
                    checks = freshness_checks(turns, scenario)
                    for name, value in checks.items():
                        self.assertTrue(value, name)
                        self.assertEqual(run['helper_checks'][name], value)
            comparisons = [comparison(c, data['runs'], data['turns']) for c in data['models']]
            self.assertEqual(data['comparisons'], comparisons)
            summary.extend({'scenario': scenario, **c} for c in comparisons)
            total_turns += len(data['turns'])
        self.assertEqual(total_turns, 144)
        self.assertEqual(json.loads((SOURCE / 'benchmarks/v0.1.2/summary.json').read_text(encoding='utf-8')), summary)

    def test_new_runner_prepares_both_methods_without_model_invocations(self):
        # Only version/Git metadata queries are mocked; demo.py really creates files.
        with tempfile.TemporaryDirectory() as temp, redirect_stdout(io.StringIO()):
            dest = Path(temp) / 'comparison'
            with patch('benchmarks.run_tokens.subprocess.check_output', return_value='test-version\n'):
                initialize(SOURCE, dest)
            manifest = json.loads((dest / 'manifest.json').read_text(encoding='utf-8'))
            self.assertEqual(manifest['arms'], ['baseline', 'improved'])
            self.assertEqual(set(manifest['versions']), {'improved'})
            self.assertRegex(manifest['date'], r'^\d{4}-\d{2}-\d{2}$')
            for client in manifest['models']:
                demo = dest / client
                direct = configure(demo, client, 'baseline', 'multi-focused')
                self.assertIn('Direct Markdown baseline', direct)
                self.assertIn('Release gates', direct)
                current = configure(demo, client, 'improved', 'multi-focused')
                self.assertIn('--compact', current)
                self.assertIn('Immediate follow-ups: ZERO calls', current)
                self.assertEqual((demo / 'obsidian_context.py').read_bytes(),
                                 (SOURCE / 'obsidian_context.py').read_bytes())


if __name__ == '__main__':
    unittest.main()
