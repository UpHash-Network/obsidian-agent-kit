import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
setup = runpy.run_path(str(SOURCE / 'setup.py'))
helper = runpy.run_path(str(SOURCE / 'obsidian_context.py'))


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name) / 'User space 日本語'
        self.home.mkdir()
        self.vault = self.home / 'Team vault'
        (self.vault / '運用').mkdir(parents=True)
        (self.vault / '運用/知識の保存方針.md').write_text('# 方針\n会社の決定だけ\n', encoding='utf-8')
        self.config = self.home / '.config/obsidian-context/config.json'
        self.env = {k: v for k, v in os.environ.items()
                    if k not in ('CODEX_HOME', 'CLAUDE_CONFIG_DIR', 'OBSIDIAN_CONTEXT_CONFIG')}
        self.call('configure', '--scope', 'team', '--vault', str(self.vault), '--policy', '運用/知識の保存方針.md')

    def tearDown(self):
        self.temp.cleanup()

    def call(self, action, *args, code=0):
        result = subprocess.run([sys.executable, str(SOURCE / 'setup.py'), action,
                                 '--home', str(self.home), *args], env=self.env,
                                capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result

    def test_fresh_install_launch_and_doctor(self):
        self.call('install')
        base, launcher = setup['installed_paths'](self.home)
        self.assertEqual((base / 'LICENSE').read_bytes(), (SOURCE / 'LICENSE').read_bytes())
        command = [str(launcher), 'team', '--query', '知識の保存方針']
        # A .cmd launch exercises Windows quoting as well as the Python helper.
        result = subprocess.run(command, env=self.env, capture_output=True,
                                text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('会社の決定だけ', result.stdout)
        self.call('doctor')
        self.assertIn('MANUAL', self.call('doctor').stdout)
        self.assertTrue((base / 'cursor-user-rule.txt').exists())

    def test_idempotent_install_preserves_existing_rules(self):
        rule = self.home / '.codex/AGENTS.md'
        rule.parent.mkdir()
        rule.write_text('# My settings\nKeep my annotations.\n', encoding='utf-8')
        self.call('install')
        first = rule.read_bytes()
        base, _ = setup['installed_paths'](self.home)
        count = len(list((base / 'backups').glob('*')))
        self.call('install')
        self.assertEqual(first, rule.read_bytes())
        self.assertEqual(count, len(list((base / 'backups').glob('*'))))
        self.assertIn('Keep my annotations.', rule.read_text(encoding='utf-8'))

    def test_legacy_migration_is_explicit_and_preserves_ownership(self):
        rule = self.home / '.claude/CLAUDE.md'
        rule.parent.mkdir()
        original = '# Other\nKeep\n\n' + setup['LEGACY'] + '\nold rule\n\n## Explicit project ownership\nKeep owner overrides\n'
        rule.write_text(original, encoding='utf-8')
        self.call('install', code=1)
        self.assertEqual(rule.read_text(encoding='utf-8'), original)
        self.assertFalse((self.home / '.codex/AGENTS.md').exists())
        self.call('install', '--migrate-legacy')
        updated = rule.read_text(encoding='utf-8')
        self.assertIn('Keep owner overrides', updated)
        self.assertIn('# Other\nKeep', updated)
        self.assertNotIn('old rule', updated)

    def test_config_scope_isolation_and_local_personal(self):
        self.call('configure', '--scope', 'personal', '--vault', str(self.home / 'Personal vault'))
        config = helper['load_config'](self.config)
        self.assertEqual(config['scopes']['personal']['sync'], 'local')
        before = self.config.read_bytes()
        self.call('configure', '--scope', 'other', '--vault', str(self.vault / 'nested'), code=1)
        self.assertEqual(before, self.config.read_bytes())

    def test_missing_policy_and_changed_install_are_detected(self):
        self.call('install')
        (self.vault / '運用/知識の保存方針.md').unlink()
        self.call('doctor', code=1)
        base, _ = setup['installed_paths'](self.home)
        (base / 'obsidian_context.py').write_text('raise SystemExit(1)', encoding='utf-8')
        self.call('doctor', code=1)

    def test_malformed_markers_rejected(self):
        for text in [setup['BEGIN'], setup['END'], setup['END'] + setup['BEGIN']]:
            with self.assertRaises(ValueError):
                setup['merge_rule'](text, 'new rule')

    def test_custom_config_environment_and_tool_homes(self):
        self.env['OBSIDIAN_CONTEXT_CONFIG'] = str(self.config)
        codex = self.home / 'Codex custom'
        claude = self.home / 'Claude custom'
        self.env.update(CODEX_HOME=str(codex), CLAUDE_CONFIG_DIR=str(claude))
        self.call('install')
        self.call('doctor')
        self.assertTrue((codex / 'AGENTS.md').exists())
        self.assertTrue((claude / 'CLAUDE.md').exists())


if __name__ == '__main__':
    unittest.main()
