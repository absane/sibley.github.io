# Publishing a blog post

The **Blog** tab at <https://sibleysec.com/blog/> is generated from Markdown files in `blog/posts/`. GitHub Actions rebuilds and deploys the site when you push to `main`. You can write in Obsidian, a text editor, or GitHub's web editor; Obsidian Publish is not needed.

## Write with Obsidian

1. In Obsidian, choose **Open folder as vault** and select this repository's `blog` folder.
2. Under **Settings → Files and links**, turn off **Use [[Wikilinks]]** and choose **Relative path to file** for new links. Set the default location for new notes to `posts` and attachments to `assets`.
3. Enable the built-in **Templates** plugin. Set its template folder to `templates`.
4. Create a note in `posts` with a filename like `my-first-post.md`. Run **Templates: Insert template** and select `post`. Obsidian fills the title and current date. You can change the title property to a more natural title, such as “My First Post”, while keeping the filename lowercase with hyphens.
5. Write the article, replace the summary, and set `draft: false` when ready to publish. Keep the draft property as a checkbox/boolean, not quoted text.

The template uses the official [Obsidian Templates variables](https://obsidian.md/help/plugins/templates) and [standard Markdown links](https://obsidian.md/help/links). Templates should be edited in Source mode so Obsidian does not rewrite their placeholder properties.

## Create a post from PowerShell instead

From the repository root:

```powershell
python scripts/new_post.py "My First Post"
```

This creates `blog/posts/my-first-post.md` with today's date and `draft: true`. It never overwrites an existing file. Open it in your editor and write your article.

## Post properties

Every post starts with:

```yaml
---
title: "My First Post"
date: 2026-10-27
summary: "A short description shown in the blog listing and link previews."
tags:
  - Research
  - AI
draft: true
---
```

Change the date to your intended publication date. It controls the displayed date and sorting; it does not schedule a future deployment. To publish, set `draft: false` and push. If `draft` is omitted, the post remains unpublished. Posts appear newest first.

The title property becomes the page's `h1`. Start the article's sections at `##`, then use `###` for subsections. Normal Markdown paragraphs, lists, blockquotes, fenced code, tables, footnotes, and images are supported. Code blocks are displayed, never executed by the builder.

The filename controls the public URL. `my-first-post.md` becomes `https://sibleysec.com/blog/my-first-post/`. Keep filenames stable after publication to preserve incoming links.

## Images and links

Save images in `blog/assets/` and embed them with a relative Markdown link:

```markdown
![A description of the screenshot](../assets/my-screenshot.png)
```

Link to another published post using its Markdown filename:

```markdown
[Read the follow-up](my-second-post.md)
[See its findings](my-second-post.md#findings)
```

The builder converts those links into public article URLs. Links to missing posts, drafts, missing local images, or invalid heading anchors fail the build, preventing a broken deployment.

Use standard Markdown for portable publishing. Obsidian-specific `[[wikilinks]]`, `![[embeds]]`, Dataview queries, Mermaid code rendering, and plugin features are not rendered by this blog. Fenced code remains plain code, including fenced Mermaid.

## Preview

One-time setup from the repository root:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Then:

```powershell
.venv\Scripts\python.exe scripts/build.py
python -m http.server 5197 --bind 127.0.0.1 --directory _site
```

Open <http://127.0.0.1:5197/blog/>. Only posts with `draft: false` appear, including in local previews. You can temporarily set it to false to inspect the full page before committing; set it back to true if it is not ready. Rebuild and refresh after edits. Stop the preview with `Ctrl+C`.

## Publish

After reviewing the post:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests
.venv\Scripts\python.exe scripts/build.py
git add blog/posts blog/assets
git commit -m "Publish: My First Post"
wsl -d Ubuntu -- git -C "/mnt/c/Users/james/Desktop/ChatGPT/Random Projects/sibley.github.io" push origin main
```

The final command uses your existing Ubuntu SSH authentication. You can also ask Codex to publish the finished post. Check the [deployment workflow](https://github.com/absane/sibley.github.io/actions) if it does not appear after deployment. The RSS feed and sitemap update automatically.

To unpublish, change `draft` back to `true` or delete the Markdown file, then commit and push. The next build removes its generated page, listing, feed item, and sitemap entry.

**Draft means hidden from the website, not private.** This GitHub repository is public, so committed Markdown is readable on GitHub, even with `draft: true`. Keep confidential drafts in a private vault until ready. All files placed in `blog/assets/` are published, so that folder is for public attachments only. Obsidian's `.obsidian/` settings folder is ignored by Git.
