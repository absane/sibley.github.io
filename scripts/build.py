"""Build the Markdown blog, validate local links, and stage public site files."""

import json
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

from blog import SITE, generate_blog

ROOT = Path(__file__).resolve().parent.parent
PAGES = ("index.html", "resume.html")


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids = set()
        self.links = []
        self.json_ld = []
        self.in_json_ld = False
        self.h1_count = 0
        source = path.read_text(encoding="utf-8")
        if "@gmail.com" in source.casefold():
            raise ValueError(f"{path.name}: personal email must not be published")
        self.feed(source)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                raise ValueError(f"Duplicate ID: {attrs['id']}")
            self.ids.add(attrs["id"])
        if tag == "h1":
            self.h1_count += 1
        for name in ("href", "src"):
            if name in attrs:
                self.links.append(attrs[name])
        if tag == "script":
            self.in_json_ld = attrs.get("type") == "application/ld+json"

    def handle_data(self, data):
        if self.in_json_ld:
            self.json_ld.append(data)

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_json_ld = False


def validate_site(output):
    pages = {path.resolve(): Page(path) for path in output.rglob("*.html")}
    for path, page in pages.items():
        name = path.relative_to(output)
        if page.h1_count != 1:
            raise ValueError(f"{name}: expected exactly one h1")
        if page.json_ld:
            json.loads("".join(page.json_ld))
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            if url.path.startswith("/"):
                raise ValueError(f"{name}: root-relative link breaks project Pages: {link}")
            destination = (path.parent / unquote(url.path)).resolve() if url.path else path
            if destination.is_dir():
                destination /= "index.html"
            if not destination.is_relative_to(output) or not destination.is_file():
                raise ValueError(f"{name}: missing or unsafe local target: {link}")
            if url.fragment and destination.suffix == ".html":
                target_page = pages.get(destination)
                if target_page is None or unquote(url.fragment) not in target_page.ids:
                    raise ValueError(f"{name}: missing anchor: {link}")
    return len(pages)


def build(root=ROOT):
    root = root.resolve()
    output = root / "_site"
    # _site is disposable build output. Verify its absolute location before cleanup.
    if output.is_symlink() or output.resolve() != root / "_site":
        raise ValueError(f"Refusing to clear unsafe output path: {output}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    for name in (*PAGES, ".nojekyll", "robots.txt"):
        shutil.copy2(root / name, output / name)
    shutil.copytree(root / "assets", output / "assets")
    posts = generate_blog(root, output)
    shutil.copytree(root / "blog" / "assets", output / "blog" / "assets",
                    ignore=shutil.ignore_patterns(".*"))
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    sitemap = ET.parse(root / "sitemap.xml")
    for post in posts:
        entry = ET.SubElement(sitemap.getroot(), f"{{{namespace}}}url")
        ET.SubElement(entry, f"{{{namespace}}}loc").text = SITE + f"/blog/{post['slug']}/"
    sitemap.write(output / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    count = validate_site(output)
    print(f"Built {len(posts)} published posts; validated {count} pages and all local links in {output}")
    return output


if __name__ == "__main__":
    build()
