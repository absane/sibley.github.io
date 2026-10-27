"""Publishing checks: draft exclusion, stale cleanup, Markdown, and local links."""

import contextlib
import io
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from build import build
import new_post


class BlogPublishingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name in ("index.html", "resume.html", ".nojekyll", "robots.txt", "sitemap.xml"):
            shutil.copy2(ROOT / name, self.root / name)
        for name in ("assets", "templates"):
            shutil.copytree(ROOT / name, self.root / name)
        (self.root / "blog" / "posts").mkdir(parents=True)
        (self.root / "blog" / "assets").mkdir()
        shutil.copytree(ROOT / "blog" / "templates", self.root / "blog" / "templates")

    def tearDown(self):
        self.temp.cleanup()

    def post(self, name, *, draft=False, date="2026-10-27", body="## Findings\n\nA real observation."):
        path = self.root / "blog" / "posts" / f"{name}.md"
        path.write_text(f'---\ntitle: "{name}"\ndate: {date}\nsummary: "A useful summary."\ndraft: {str(draft).lower()}\ntags: [Research]\n---\n\n{body}\n', encoding="utf-8")
        return path

    def run_build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return build(self.root)

    def test_empty_blog_has_real_empty_state_and_valid_feed(self):
        output = self.run_build()
        self.assertIn("No posts published yet", (output / "blog" / "index.html").read_text(encoding="utf-8"))
        self.assertEqual([], ET.parse(output / "blog" / "feed.xml").findall(".//item"))
        self.assertFalse((output / "blog" / "posts").exists())

    def test_markdown_tables_code_images_and_newest_first(self):
        self.post("older", date="2026-10-01")
        self.post("newer", body='## Findings\n\n```html\n<script>example()</script>\n```\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n![Diagram](../assets/diagram.svg)\n\n## Takeaways\n\nA conclusion.')
        (self.root / "blog" / "assets" / "diagram.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        output = self.run_build()
        page = (output / "blog" / "newer" / "index.html").read_text(encoding="utf-8")
        self.assertIn("&lt;script&gt;", page)
        self.assertIn("<table>", page)
        self.assertIn("On this page", page)
        index = (output / "blog" / "index.html").read_text(encoding="utf-8")
        self.assertLess(index.index('href="newer/"'), index.index('href="older/"'))
        self.assertEqual(2, len(ET.parse(output / "blog" / "feed.xml").findall(".//item")))

    def test_draft_hidden_and_unpublishing_removes_stale_html_feed_and_sitemap(self):
        self.post("hidden", draft=True)
        self.post("visible")
        output = self.run_build()
        self.assertTrue((output / "blog" / "visible" / "index.html").is_file())
        self.post("visible", draft=True)
        output = self.run_build()
        for slug in ("hidden", "visible"):
            self.assertFalse((output / "blog" / slug).exists())
            self.assertNotIn(f"/blog/{slug}/", (output / "sitemap.xml").read_text())
            self.assertNotIn(f"/blog/{slug}/", (output / "blog" / "feed.xml").read_text())

    def test_markdown_post_links_resolve_and_draft_targets_fail(self):
        self.post("first", body="## Notes\n\n[Next](second.md#findings)")
        self.post("second")
        output = self.run_build()
        self.assertIn('href="../second/#findings"', (output / "blog" / "first" / "index.html").read_text(encoding="utf-8"))
        self.post("second", draft=True)
        with self.assertRaisesRegex(ValueError, "missing or still a draft"):
            self.run_build()

    def test_invalid_properties_and_broken_images_block_publication(self):
        source = self.post("broken")
        source.write_text(source.read_text().replace("draft: false", 'draft: "false"'))
        with self.assertRaisesRegex(ValueError, "without quotes"):
            self.run_build()
        self.post("broken", body="## Image\n\n![Missing](../assets/missing.png)")
        with self.assertRaisesRegex(ValueError, "missing or unsafe local target"):
            self.run_build()

    def test_multiple_page_titles_and_personal_email_block_publication(self):
        self.post("invalid", body="# Extra title\n\nText")
        with self.assertRaisesRegex(ValueError, "exactly one h1"):
            self.run_build()
        self.post("invalid", body="## Contact\n\nprivate" + "@gmail.com")
        with self.assertRaisesRegex(ValueError, "personal email"):
            self.run_build()

    def test_new_post_helper_creates_valid_draft_and_never_overwrites(self):
        with patch.object(new_post, "ROOT", self.root), contextlib.redirect_stdout(io.StringIO()):
            new_post.create_post('Testing "quoted" titles')
            source = self.root / "blog" / "posts" / "testing-quoted-titles.md"
            self.assertIn("draft: true", source.read_text())
            with self.assertRaises(FileExistsError):
                new_post.create_post('Testing "quoted" titles')
        output = self.run_build()
        self.assertFalse((output / "blog" / "testing-quoted-titles").exists())


if __name__ == "__main__":
    unittest.main()
