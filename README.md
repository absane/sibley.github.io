# James Sibley — Independent Security Consulting

A static professional site and printable public résumé, built for GitHub Pages. No framework, package installation, analytics, remote fonts, or backend is required. All page content works without JavaScript; JavaScript updates the copyright year and opens the browser print dialog.

## Preview

From this repository:

```powershell
python scripts/build.py
python -m http.server 5197 --bind 127.0.0.1 --directory _site
```

Open <http://127.0.0.1:5197/>. The résumé's **Print / Save PDF** button opens your browser's print dialog. Choose **Save as PDF** for a portable copy. Disable browser headers/footers for a cleaner result.

## Publish on GitHub Pages

1. Open [Settings → Pages](https://github.com/absane/sibley.github.io/settings/pages).
2. Under **Build and deployment → Source**, select **GitHub Actions**.
3. Push to `main`, or run **Deploy professional site** from the repository's [Actions tab](https://github.com/absane/sibley.github.io/actions).

The workflow validates the JavaScript, checks local links and anchors, stages only public assets, and deploys `_site/`. Git metadata, documentation, scripts, and the supplied LinkedIn export are excluded from the deployment artifact.

Public address:

<https://sibleysec.com/>

The custom domain is configured in GitHub Pages settings. Canonical links, structured profile data, and `sitemap.xml` use this address. The published contact address is `james@sibleysec.com`, as specified by the owner; personal contact information from the source export is not used on the site.

GitHub's original project address:

<https://absane.github.io/sibley.github.io/>

The repository is owned by `absane`; its name does **not** assign the `sibley.github.io` hostname. For the account-root address `https://absane.github.io/`, the repository would need to be named `absane.github.io`. A custom domain can also be configured through GitHub Pages. All local asset and navigation links are relative, so the site supports either a project subpath or a custom-domain root.

## Update content

- `index.html`: introduction, services, career summary, articles, and contact information.
- `resume.html`: professional résumé, including earlier experience, education, credentials, recognition, and languages.
- `assets/styles.css`: design tokens, layout, responsive breakpoints, and print styles.
- `assets/favicon.svg`: vector monogram.
- `assets/site.js`: optional year and print helpers.

After editing, run `python scripts/build.py` and `node --check assets/site.js`, inspect the preview at desktop and mobile sizes, then commit the completed change.

## Content provenance

Career dates, job titles, education, certifications, recognition, location, and contact details were supplied in the user's LinkedIn `Profile.pdf` export on October 27, 2026. Copy is condensed for the website; it is not a verbatim export. The source PDF is left outside this repository, including its tracking parameters and export metadata.

The live LinkedIn profile and activity feed blocked automated access. The writing section therefore links to confirmed public articles rather than claiming to reproduce the LinkedIn sharing feed. Article titles and dates were verified against these publisher pages:

- [AI and social engineering](https://versprite.com/resources/blog/the-intersection-of-artificial-intelligence-and-social-engineering-next-generation-threats/) — September 28, 2023.
- [Attacking Your Assumptions](https://versprite.com/resources/blog/attacking-your-assumptions-know-your-security-blind-spots/) — August 15, 2022.
- [Physical security](https://versprite.com/resources/blog/preventing-physical-security-attacks-against-business/) — August 2, 2021.
- [Security awareness blind spots](https://versprite.com/resources/blog/security-awareness-training-vs-social-engineering-attacks/) — March 4, 2021.
- [WD My Cloud command injection](https://versprite.com/resources/blog/command-injection-in-the-wd-my-cloud-nas/) — September 16, 2015. This publication is listed in the supplied profile; the publisher currently credits VerSprite collectively.

The Exploit Database author link (`https://www.exploit-db.com/author/?a=6369`) was extracted from actual PDF link annotations. Its endpoint returned HTTP 502 during initial verification; availability is not guaranteed. The obsolete personal blog link has been removed at the owner's request. Other profile publication titles without verified destination URLs were not given fabricated links.
