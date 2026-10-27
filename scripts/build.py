"""Validate local links and stage only public site files. No dependencies."""

import json
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

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
        self.feed(path.read_text(encoding="utf-8"))

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


def build():
    pages = {name: Page(ROOT / name) for name in PAGES}
    for name, page in pages.items():
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
            destination = (ROOT / unquote(url.path or name)).resolve()
            if not destination.is_relative_to(ROOT) or not destination.is_file():
                raise ValueError(f"{name}: missing or unsafe local target: {link}")
            if url.fragment and destination.suffix == ".html":
                target_page = pages.get(destination.name)
                if target_page is None or unquote(url.fragment) not in target_page.ids:
                    raise ValueError(f"{name}: missing anchor: {link}")
    output = ROOT / "_site"
    output.mkdir(exist_ok=True)
    for name in (*PAGES, ".nojekyll"):
        shutil.copy2(ROOT / name, output / name)
    shutil.copytree(ROOT / "assets", output / "assets", dirs_exist_ok=True)
    print(f"Validated {len(pages)} pages and all local links; staged public site in {output}")


if __name__ == "__main__":
    build()
