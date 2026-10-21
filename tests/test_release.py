from pathlib import Path
import re
import unittest

SOURCE = Path(__file__).resolve().parents[1]


class ReleaseTests(unittest.TestCase):
    def test_local_document_links_resolve(self):
        roots = [SOURCE / 'README.md', SOURCE / 'README.ja.md',
                 SOURCE / 'CONTRIBUTING.md',
                 *list((SOURCE / 'docs').rglob('*.md')),
                 *list((SOURCE / 'benchmarks').rglob('*.md')),
                 *list((SOURCE / 'examples/demo-vault').rglob('*.md'))]
        for file in roots:
            text = file.read_text(encoding='utf-8')
            targets = re.findall(r'\]\(([^)]+)\)', text) + re.findall(r'src="([^"]+)"', text)
            for target in targets:
                if '://' in target or target.startswith('#'):
                    continue
                self.assertTrue((file.parent / target.split('#')[0]).exists(),
                                f'{file.name}: broken link {target}')

    def test_fictional_note_metadata(self):
        for path in (SOURCE / 'examples/demo-vault').rglob('*.md'):
            text = path.read_text(encoding='utf-8')
            self.assertTrue(text.startswith('---\n'))
            frontmatter = text.split('---', 2)[1]
            for key in ['scope', 'asset_type', 'status', 'project', 'date']:
                self.assertRegex(frontmatter, r'(?m)^' + key + ': .+')


if __name__ == '__main__':
    unittest.main()
