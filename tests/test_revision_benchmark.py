"""Freshness evidence must not pass from status labels or correct guesses alone."""
from copy import deepcopy
import unittest

from benchmarks.aggregate_revision import freshness_checks


class RevisionEvidenceTests(unittest.TestCase):
    def rows(self):
        paths = ['Policies/Knowledge policy.md', 'Projects/Lighthouse.md']
        rows = []
        for stage in range(1, 5):
            rows.append({'stage': stage, 'tool_calls': 0 if stage == 2 else 1,
                         'helper_statuses': [] if stage == 2 else [
                             {'path': p, 'sha256': 'b' * 64 if stage == 4 and i == 1 else 'a' * 64,
                              'status': 'CONTENT' if stage == 1 or (stage == 4 and i == 1) else 'UNCHANGED'}
                             for i, p in enumerate(paths)]})
        return rows

    def test_missing_policy_and_stale_hash_fail(self):
        rows = self.rows()
        self.assertTrue(all(freshness_checks(rows, 'single-full').values()))
        bad = deepcopy(rows)
        bad[3]['helper_statuses'][1]['sha256'] = 'a' * 64
        self.assertFalse(freshness_checks(bad, 'single-full')['changed_note_only_content'])
        bad = deepcopy(rows)
        bad[2]['helper_statuses'].pop(0)
        self.assertFalse(freshness_checks(bad, 'single-full')['unchanged_all_unchanged'])

    def test_unrelated_note_or_unexpected_hash_change_fails(self):
        bad = self.rows()
        bad[3]['helper_statuses'][0]['sha256'] = 'c' * 64
        self.assertFalse(freshness_checks(bad, 'single-full')['changed_note_only_content'])
        bad = self.rows()
        bad[0]['helper_statuses'].append({'path': 'Projects/Unrelated.md', 'sha256': 'd' * 64, 'status': 'CONTENT'})
        self.assertFalse(freshness_checks(bad, 'single-full')['all_required_hashes_present'])
