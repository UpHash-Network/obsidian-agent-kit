"""Accounting invariants: prevent double-counting or concealing missing usage."""
import unittest
from benchmarks.aggregate_tokens import normalize, reduction


class AccountingTests(unittest.TestCase):
    def test_codex_cumulative_cached_input_is_counted_once(self):
        first = {'input_tokens': 100, 'cached_input_tokens': 60, 'output_tokens': 10}
        second = {'input_tokens': 250, 'cached_input_tokens': 180, 'output_tokens': 30}
        a, b = normalize('codex', first), normalize('codex', second, first)
        self.assertEqual(a['total'] + b['total'], 280)
        self.assertEqual(b['regular_input'], 30)
        self.assertEqual(b['cache_read'], 120)

    def test_claude_sums_auxiliary_model_and_cache(self):
        model = {'inputTokens': 2, 'cacheCreationInputTokens': 3,
                 'cacheReadInputTokens': 5, 'outputTokens': 7}
        self.assertEqual(normalize('claude', {'main': model, 'aux': model})['total'], 34)

    def test_cursor_fields_and_missing_usage(self):
        self.assertEqual(normalize('cursor', {'inputTokens': 2, 'cacheWriteTokens': 3,
                         'cacheReadTokens': 5, 'outputTokens': 7})['total'], 17)
        with self.assertRaises(ValueError):
            normalize('cursor', None)
        with self.assertRaises(KeyError):
            normalize('cursor', {'inputTokens': 2})

    def test_increases_are_negative_savings(self):
        self.assertEqual(reduction(100, 125), -25)
        self.assertEqual(reduction(100, 75), 25)
        with self.assertRaises(ValueError):
            normalize('codex', {'input_tokens': 1, 'cached_input_tokens': 2, 'output_tokens': 0})
