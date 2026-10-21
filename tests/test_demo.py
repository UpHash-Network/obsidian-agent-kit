import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]


class DemoTests(unittest.TestCase):
    def test_real_cli_roundtrip_and_three_rule_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'Demo space 日本語'
            def run(script, *args, code=0):
                result = subprocess.run([sys.executable, str(SOURCE / script), *map(str, args)],
                                        capture_output=True, text=True, encoding='utf-8',
                                        env={**os.environ, 'PYTHONIOENCODING': 'ascii'})
                self.assertEqual(result.returncode, code, result.stdout + result.stderr)
                return result.stdout
            run('demo.py', 'init', '--dest', dest)
            license_text = (SOURCE / 'LICENSE').read_bytes()
            self.assertEqual((dest / 'LICENSE').read_bytes(), license_text)
            self.assertEqual((dest / 'vault/LICENSE').read_bytes(), license_text)
            self.assertTrue((dest / 'vault/Welcome.ja.md').exists())
            self.assertEqual((dest / 'vault/Assets/UPHASH/logo.png').read_bytes(),
                             (SOURCE / 'examples/demo-vault/Assets/UPHASH/logo.png').read_bytes())
            run('demo.py', 'init', '--dest', dest, code=1)
            rules = [dest / 'codex/AGENTS.md', dest / 'claude/CLAUDE.md',
                     dest / 'cursor/.cursor/rules/obsidian-knowledge.mdc']
            for rule in rules:
                text = rule.read_text(encoding='utf-8')
                self.assertIn('Immediate follow-ups: ZERO calls', text)
                self.assertIn('--check', text)
                self.assertIn('scope `demo`', text)
            config = dest / 'config.json'
            initial = run('obsidian_context.py', 'demo', '--config', config, '--query', 'Lighthouse')
            self.assertIn('**blue**', initial)
            self.assertNotIn('orange', initial)
            note = dest / 'vault/Projects/Lighthouse.md'
            digest = hashlib.sha256(note.read_bytes()).hexdigest()
            before = note.stat()
            unchanged = run('obsidian_context.py', 'demo', '--config', config,
                            '--check', 'Projects/Lighthouse.md=' + digest)
            self.assertEqual(json.loads(unchanged)['status'], 'UNCHANGED')
            run('demo.py', 'change', '--dest', dest)
            self.assertEqual(note.stat().st_mtime_ns, before.st_mtime_ns)
            self.assertEqual(note.stat().st_size, before.st_size)
            changed = run('obsidian_context.py', 'demo', '--config', config,
                          '--check', 'Projects/Lighthouse.md=' + digest)
            self.assertIn('**teal**', changed)
            self.assertNotIn('UNCHANGED', changed)
            self.assertIn('Human annotations', changed)


if __name__ == '__main__':
    unittest.main()
