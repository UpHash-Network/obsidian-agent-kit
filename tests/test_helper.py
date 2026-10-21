import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

module = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'obsidian_context.py'))

class HelperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'vault'
        self.root.mkdir()
        self.config = self.root.parent / 'config.json'
        self.config.write_text(json.dumps({'version': 1, 'scopes': {'personal': {'root': str(self.root), 'policy': '知識の保存方針.md', 'sync': 'local', 'owners': []}}}), encoding='utf-8')
        self.note = self.root / 'test.md'
        self.write_note('---\nscope: personal\n---\n# 現在の決定\nReviewer A; MARKER-A\n')
        (self.root / '知識の保存方針.md').write_text('# 方針\nLocal only\n', encoding='utf-8')
    def write_note(self, text):
        self.note.write_text(text, encoding='utf-8')
    def tearDown(self):
        self.temp.cleanup()
    def call(self, *args):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            status = module['run'](['personal', '--config', str(self.config), *args])
        return status, stream.getvalue()
    def baseline(self):
        code, text = self.call('--file', 'test.md')
        self.assertEqual(code, 0, text)
        return json.loads(text.splitlines()[0])['sha256']
    def test_query_reads_only_exact_note_and_policy(self):
        (self.root / 'test-other.md').write_text('UNRELATED_SECRET')
        code, text = self.call('--query', 'test')
        self.assertEqual(code, 0, text)
        self.assertIn('MARKER-A', text)
        self.assertIn('Local only', text)
        self.assertNotIn('UNRELATED_SECRET', text)
    def test_unchanged_has_no_body_and_touch_does_not_resend(self):
        digest = self.baseline()
        os.utime(self.note, None)
        code, text = self.call('--check', 'test.md=' + digest)
        self.assertEqual(code, 0, text)
        self.assertEqual(json.loads(text)['status'], 'UNCHANGED')
        self.assertNotIn('MARKER-A', text)
    def test_same_mtime_same_size_content_change_detected(self):
        digest = self.baseline()
        stat = self.note.stat()
        self.write_note(self.note.read_text(encoding='utf-8').replace('MARKER-A', 'MARKER-B'))
        os.utime(self.note, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        self.assertEqual(self.note.stat().st_size, stat.st_size)
        code, text = self.call('--check', 'test.md=' + digest)
        self.assertEqual(code, 0, text)
        self.assertIn('MARKER-B', text)
        self.assertNotIn('UNCHANGED', text)
    def test_force_rereads_for_conflict_or_missing_context(self):
        digest = self.baseline()
        code, text = self.call('--check', 'test.md=' + digest, '--force')
        self.assertEqual(code, 0, text)
        self.assertIn('MARKER-A', text)
    def test_edit_during_read_retries_and_returns_fresh_content(self):
        original = os.fstat
        calls = 0
        def change_after_read(fd):
            nonlocal calls
            calls += 1
            if calls == 2:
                self.write_note('# Current\nMARKER-B with a new length\n')
            return original(fd)
        with patch.object(os, 'fstat', side_effect=change_after_read):
            code, text = self.call('--file', 'test.md')
        self.assertEqual(code, 0, text)
        self.assertIn('MARKER-B', text)
        self.assertNotIn('MARKER-A', text)
    def test_missing_note_is_error_not_unchanged(self):
        digest = self.baseline()
        self.note.unlink()
        code, text = self.call('--check', 'test.md=' + digest)
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(text)['status'], 'ERROR')
    def test_other_scope_symlink_and_traversal_rejected(self):
        outside = self.root.parent / 'private.md'
        outside.write_text('PRIVATE_BODY')
        for relative in ['../private.md', str(outside)]:
            code, text = self.call('--file', relative)
            self.assertEqual(code, 1)
            self.assertNotIn('PRIVATE_BODY', text)
    def test_symlink_outside_scope_rejected(self):
        outside = self.root.parent / 'private.md'
        outside.write_text('PRIVATE_BODY')
        try:
            (self.root / 'link.md').symlink_to(outside)
        except OSError:
            self.skipTest('Symlink creation requires Windows Developer Mode or privilege')
        code, text = self.call('--file', 'link.md')
        self.assertEqual(code, 1)
        self.assertNotIn('PRIVATE_BODY', text)

    def test_large_note_focused_section_and_partial_notice(self):
        self.write_note('---\nscope: personal\n---\n# History\n' + 'OLD\n' * 2000 + '# 現在の決定\nReviewer B; LATEST\n')
        code, text = self.call('--file', 'test.md', '--chars', '500')
        self.assertEqual(code, 0, text)
        self.assertIn('LATEST', text)
        self.assertIn('PARTIAL', text)
        self.assertNotIn('OLD\n', text)
    def test_ambiguous_query_returns_candidates_not_bodies(self):
        (self.root/'test-copy.md').write_text('NEVER_READ')
        code, text = self.call('--query', 'tes')
        self.assertEqual(code, 0, text)
        self.assertIn('candidates', text)
        self.assertNotIn('NEVER_READ', text)
        self.assertNotIn('MARKER-A', text)

    def test_compact_still_hashes_omitted_content_with_same_metadata(self):
        self.write_note('# Current\nVisible A\n# Archive\nHidden A\n')
        code, text = self.call('--compact', '--file', 'test.md', '--section', 'Current')
        self.assertEqual(code, 0)
        header = json.loads(text.splitlines()[0])
        self.assertNotIn('mtime_ns', header)
        self.assertNotIn('size', header)
        self.assertNotIn('Hidden A', text)
        stat = self.note.stat()
        self.write_note(self.note.read_text().replace('Hidden A', 'Hidden B'))
        os.utime(self.note, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        self.assertEqual(self.note.stat().st_size, stat.st_size)
        code, updated = self.call('--compact', '--check', 'test.md=' + header['sha256'], '--section', 'Current')
        current = json.loads(updated.splitlines()[0])
        self.assertEqual(code, 0)
        self.assertEqual(current['status'], 'CONTENT')
        self.assertNotEqual(current['sha256'], header['sha256'])
        self.assertIn('Visible A', updated)
        code, same = self.call('--compact', '--check', 'test.md=' + current['sha256'])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(same)['status'], 'UNCHANGED')
        code, forced = self.call('--compact', '--check', 'test.md=' + current['sha256'], '--force', '--section', 'Archive')
        self.assertEqual(code, 0)
        self.assertIn('Hidden B', forced)

    def test_selected_section_keeps_children_and_fenced_heading_text(self):
        self.write_note('# Project\n## Current\nParent\n### Limits\nChild\n```md\n## Fake end\n```\nAfter fence\n## Archive\nDo not include\n')
        code, text = self.call('--file', 'test.md', '--section', '^## Current$')
        self.assertEqual(code, 0)
        self.assertIn('Child', text)
        self.assertIn('After fence', text)
        self.assertNotIn('Do not include', text)
        self.assertIn('selected sections complete', text)

    def test_truncated_or_missing_selection_is_not_complete(self):
        self.write_note('# Current\n' + 'Important fact\n' * 200 + '# Archive\nOld fact\n')
        code, text = self.call('--file', 'test.md', '--section', 'Current', '--chars', '100')
        self.assertEqual(code, 0)
        self.assertIn('selected content truncated', text)
        self.assertNotIn('selected sections complete', text)
        code, text = self.call('--file', 'test.md', '--section', 'Missing')
        self.assertEqual(code, 0)
        self.assertIn('no heading matched', text)
        self.assertNotIn('Important fact', text)

    def test_compact_batch_does_not_filter_policy_with_project_headings(self):
        code, text = self.call('--compact', '--file', 'test.md', '--file', '知識の保存方針.md', '--section', '現在')
        self.assertEqual(code, 0)
        self.assertIn('MARKER-A', text)
        self.assertIn('Local only', text)

    def test_three_long_notes_fit_one_focused_batch(self):
        from benchmarks.long_notes import note
        for i, name in enumerate(['Lighthouse', 'Orchard', 'Atlas']):
            (self.root / (name + '.md')).write_text(note(name, i))
        code, text = self.call('--compact', '--file', '知識の保存方針.md', '--file', 'Lighthouse.md',
                               '--file', 'Orchard.md', '--file', 'Atlas.md', '--section', 'Current decisions|Release gates')
        self.assertEqual(code, 0)
        for value in ['security sign-off', 'accessibility review', 'restore test']:
            self.assertIn(value, text)
        self.assertEqual(text.count('selected sections complete'), 3)
        self.assertNotIn('Archived work item', text)
        self.assertNotIn('truncated', text)

if __name__ == '__main__':
    unittest.main()
