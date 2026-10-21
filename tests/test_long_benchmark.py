"""Protect answer validation and the tail-section/truncation measurement."""
import json
import unittest

from benchmarks.aggregate_long_notes import quality, tool_outputs
from benchmarks.long_notes import expected, note
from obsidian_context import excerpt


class LongBenchmarkTests(unittest.TestCase):
    def test_needed_gate_is_outside_default_excerpt_but_available_when_focused(self):
        source = note('Lighthouse', 0)
        default, coverage = excerpt(source, 6000, None)
        self.assertEqual(coverage, 'partial')
        self.assertNotIn('security sign-off', default)
        focused, _ = excerpt(source, 6000, 'Current decisions|Release gates')
        self.assertIn('security sign-off', focused)
        self.assertIn('**Mira**', focused)

    def test_stale_and_cross_project_answers_fail(self):
        answer = expected('multi-full', 4)
        self.assertTrue(quality(json.dumps(answer), 'multi-full', 4)['exact_facts_and_format'])
        answer['projects'][0]['channel'] = 'blue'
        self.assertFalse(quality(json.dumps(answer), 'multi-full', 4)['exact_facts_and_format'])
        answer = expected('multi-full', 4)
        answer['projects'][1]['blocker'] = 'security sign-off'
        self.assertFalse(quality(json.dumps(answer), 'multi-full', 4)['exact_facts_and_format'])

    def test_cursor_shell_output_is_not_counted_twice(self):
        events = [{'type': 'tool_call', 'subtype': 'completed', 'tool_call': {
            'shellToolCall': {'result': {'success': {
                'stdout': 'abc', 'stderr': '', 'interleavedOutput': 'abc'}}}}}]
        self.assertEqual(list(tool_outputs('cursor', events)), ['abc'])

    def test_commentary_is_not_mistaken_for_wrong_facts(self):
        text = 'Reading notes.\n' + json.dumps(expected('single-full', 1))
        result = quality(text, 'single-full', 1)
        self.assertTrue(result['exact_facts'])
        self.assertFalse(result['exact_facts_and_format'])
