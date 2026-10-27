"""Create an unpublished Markdown post from the Obsidian-compatible template."""

import argparse
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def slugify(title):
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")


def create_post(title):
    slug = slugify(title)
    if not slug:
        raise ValueError("Choose a title containing letters or numbers")
    destination = ROOT / "blog" / "posts" / f"{slug}.md"
    template = (ROOT / "blog" / "templates" / "post.md").read_text(encoding="utf-8")
    template = template.replace('"{{title}}"', json.dumps(title, ensure_ascii=False), 1)
    template = template.replace("{{date:YYYY-MM-DD}}", date.today().isoformat())
    with destination.open("x", encoding="utf-8") as post:
        post.write(template)
    print(f"Created draft: {destination}")
    print("Edit the Markdown file, then change draft: true to draft: false when ready.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("title", help="Title of the new post")
    args = parser.parse_args()
    try:
        create_post(args.title)
    except (ValueError, FileExistsError) as error:
        parser.exit(1, f"{error}\n")
