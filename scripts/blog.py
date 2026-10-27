"""Render author-owned Markdown files into a static blog and RSS feed."""

import html
import json
import math
import re
from datetime import date, datetime, time, timezone
from pathlib import Path
from string import Template
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

import markdown
import yaml

SITE = "https://sibleysec.com"


def read_posts(root):
    posts = []
    slugs = set()
    for source in sorted((root / "blog" / "posts").glob("*.md")):
        text = source.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        parts = text.split("\n---\n", 1) if text.startswith("---\n") else []
        if len(parts) != 2:
            raise ValueError(f"{source.name}: start the file with YAML properties between --- lines")
        metadata = yaml.safe_load(parts[0][4:])
        if not isinstance(metadata, dict):
            raise ValueError(f"{source.name}: properties must be a YAML mapping")
        draft = metadata.get("draft", True)
        if type(draft) is not bool:
            raise ValueError(f"{source.name}: draft must be true or false, without quotes")
        if draft:
            continue
        slug = source.stem
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in {"assets", "index"}:
            raise ValueError(f"{source.name}: use a lowercase filename with hyphens, such as my-first-post.md")
        if slug in slugs:
            raise ValueError(f"{source.name}: duplicate post URL")
        slugs.add(slug)
        for key in ("title", "summary"):
            if not isinstance(metadata.get(key), str) or not metadata[key].strip():
                raise ValueError(f"{source.name}: provide a non-empty {key}")
        published = metadata.get("date")
        if isinstance(published, str):
            try:
                published = date.fromisoformat(published)
            except ValueError:
                published = None
        if type(published) is not date:
            raise ValueError(f"{source.name}: date must use YYYY-MM-DD")
        tags = metadata.get("tags", []) or []
        if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            raise ValueError(f"{source.name}: tags must be a YAML list of text labels")
        body = parts[1].strip()
        if not body:
            raise ValueError(f"{source.name}: published posts need a body")
        posts.append({"source": source.resolve(), "slug": slug, "title": metadata["title"].strip(),
                      "summary": metadata["summary"].strip(), "date": published,
                      "tags": tags, "body": body,
                      "minutes": max(1, math.ceil(len(re.findall(r"\b\w+\b", body)) / 200))})
    return sorted(posts, key=lambda post: (post["date"], post["slug"]), reverse=True)


def formatted_date(value):
    return f"{value.strftime('%B')} {value.day}, {value.year}"


def tags_html(tags):
    return "".join(f'<span class="post-tag">{html.escape(tag)}</span>' for tag in tags)


def render_body(post, posts):
    converter = markdown.Markdown(extensions=["extra", "toc", "sane_lists"])
    rendered = converter.convert(post["body"])
    by_source = {item["source"]: item for item in posts}

    def rewrite(match):
        target = html.unescape(match.group(1))
        url = urlsplit(target)
        if url.scheme or url.netloc or not url.path.endswith(".md"):
            return match.group(0)
        destination = (post["source"].parent / unquote(url.path)).resolve()
        if destination not in by_source:
            raise ValueError(f"{post['slug']}: linked post is missing or still a draft: {target}")
        link = f"../{by_source[destination]['slug']}/"
        if url.fragment:
            link += "#" + url.fragment
        return f'href="{html.escape(link, quote=True)}"'

    rendered = re.sub(r'href="([^"]*)"', rewrite, rendered)
    toc = ""
    if len(converter.toc_tokens) > 1:
        toc = f'<details class="post-toc"><summary>On this page</summary>{converter.toc}</details>'
    return rendered, toc


def write_page(template, destination, *, title, description, canonical, content, root, blog_prefix, schema, article=False):
    document = template.substitute(title=html.escape(title, quote=True),
        description=html.escape(description, quote=True), canonical=html.escape(canonical, quote=True),
        og_type="article" if article else "website", content=content, root=root,
        blog_prefix=blog_prefix, year=date.today().year,
        structured_data=json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c"))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(document, encoding="utf-8")


def generate_blog(root, output):
    posts = read_posts(root)
    template = Template((root / "templates" / "blog-page.html").read_text(encoding="utf-8"))
    intro = '<section class="blog-intro"><p class="eyebrow">Research / Experiments / Perspectives</p><h1>Field notes<span class="wordmark-dot">.</span></h1><p>Offensive security, artificial intelligence, and the unexpected ways systems fail.</p><a class="text-link" href="feed.xml">Subscribe via RSS <span aria-hidden="true">↗</span></a></section>'
    if posts:
        cards = []
        for post in posts:
            cards.append(f'''<article class="post-card"><div class="post-card-meta"><time datetime="{post['date'].isoformat()}">{formatted_date(post['date'])}</time><span>{post['minutes']} min read</span></div><div class="post-tags">{tags_html(post['tags'])}</div><h2><a href="{post['slug']}/">{html.escape(post['title'])}</a></h2><p>{html.escape(post['summary'])}</p><a class="text-link" href="{post['slug']}/" aria-label="Read {html.escape(post['title'], quote=True)}">Read article <span aria-hidden="true">↗</span></a></article>''')
        listing = '<section class="post-grid" aria-label="Published articles">' + "".join(cards) + "</section>"
    else:
        listing = '<section class="blog-empty"><span class="notebook-mark" aria-hidden="true">[ + ]</span><div><p class="eyebrow">The notebook is open</p><h2>No posts published yet.</h2><p>New articles will appear here. In the meantime, explore my published research and perspectives.</p><a class="text-link" href="../index.html#writing">Read selected publications <span aria-hidden="true">↗</span></a></div></section>'
    write_page(template, output / "blog" / "index.html", title="Blog — James Sibley",
        description="Field notes on offensive security, artificial intelligence, and security research by James Sibley.",
        canonical=SITE + "/blog/", content=intro + listing, root="..", blog_prefix=".",
        schema={"@context": "https://schema.org", "@type": "Blog", "name": "Field notes — James Sibley", "url": SITE + "/blog/"})
    for post in posts:
        rendered, toc = render_body(post, posts)
        url = SITE + f"/blog/{post['slug']}/"
        content = f'''<article class="blog-post"><header class="post-header"><a class="text-link" href="../">← All posts</a><div class="post-tags">{tags_html(post['tags'])}</div><h1>{html.escape(post['title'])}</h1><p class="post-summary">{html.escape(post['summary'])}</p><p class="post-byline">James Sibley <span aria-hidden="true">·</span> <time datetime="{post['date'].isoformat()}">{formatted_date(post['date'])}</time> <span aria-hidden="true">·</span> {post['minutes']} min read</p></header>{toc}<div class="post-body">{rendered}</div><footer class="post-end"><a class="text-link" href="../">← Back to all posts</a><a class="text-link" href="mailto:james@sibleysec.com">Discuss this article <span aria-hidden="true">↗</span></a></footer></article>'''
        write_page(template, output / "blog" / post["slug"] / "index.html",
            title=post["title"] + " — James Sibley", description=post["summary"], canonical=url,
            content=content, root="../..", blog_prefix="..", article=True,
            schema={"@context": "https://schema.org", "@type": "BlogPosting", "headline": post["title"],
                    "description": post["summary"], "datePublished": post["date"].isoformat(), "url": url,
                    "mainEntityOfPage": url, "author": {"@type": "Person", "name": "James Sibley", "url": SITE + "/"}})
    write_feed(posts, output)
    return posts


def write_feed(posts, output):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    for key, value in {"title": "Field notes — James Sibley", "link": SITE + "/blog/",
                       "description": "Offensive security, AI, and security research.", "language": "en-us"}.items():
        ET.SubElement(channel, key).text = value
    for post in posts:
        item = ET.SubElement(channel, "item")
        url = SITE + f"/blog/{post['slug']}/"
        for key, value in {"title": post["title"], "link": url, "guid": url, "description": post["summary"],
                           "pubDate": datetime.combine(post["date"], time(), timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")}.items():
            ET.SubElement(item, key).text = value
        for tag in post["tags"]:
            ET.SubElement(item, "category").text = tag
    ET.ElementTree(rss).write(output / "blog" / "feed.xml", encoding="utf-8", xml_declaration=True)
