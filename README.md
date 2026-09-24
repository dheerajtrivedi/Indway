# Indway

Marketing site for Indway, an LT panel manufacturer (PCC, MCC, APFC, distribution boards, AMF panels and feeder pillars).

The site is static HTML. The homepage hero is an interactive 3D model of an LT panel lineup, built with [three.js](https://threejs.org/), that visitors can explore through hotspots and a guided tour.

## Project structure

```
index.html          Homepage: markup, styles and the three.js scene
lt-panels/          SEO landing pages for the range (no three.js)
  index.html        Range overview and comparison table
  <slug>/index.html One page per panel: pcc-panel, mcc-panel, apfc-panel,
                    distribution-board, amf-synchronising-panel, feeder-pillar
sitemap.xml         Lists every page; update <lastmod> when content changes
robots.txt          Points crawlers to the sitemap
assets/
  panels.css        Shared styles for the lt-panels pages
  indway-logo.webp  Logo used in the nav, footer and on the 3D panel
  indway-logo.png   PNG version of the logo
  indway-mark.png   Favicon
  lt-panel.webp     Static hero image (no longer used; the hero shows an inline SVG loader)
INDWAY_logo.jpg     Original logo artwork (source file, not used by the page)
LTPANEL.png         Original panel image (source file, not used by the page)
```

## Page sections

| Anchor     | Content                                              |
|------------|------------------------------------------------------|
| `#scene`   | Hero with the interactive 3D panel                   |
| `#range`   | Product range: PCC, MCC, APFC, DBs, AMF, feeder pillars |
| `#process` | Process: review through commissioning                |
| `#contact` | Enquiry details and "Email your SLD" button          |

## Running locally

There is no build step or dependencies to install. The page loads three.js as an ES module, so it has to be served over HTTP rather than opened as a `file://` URL:

```sh
python3 -m http.server 8000
# then open http://localhost:8000
```

Any static file server works (for example `npx serve`).

## External dependencies

Loaded at runtime, so the page needs an internet connection:

- **three.js 0.170.0** from jsDelivr, via the import map in `index.html`
- **Archivo** font from Google Fonts

## Deployment

Upload `index.html` and the `assets/` folder to any static host (GitHub Pages, Netlify, Vercel, S3 and so on). The root-level `INDWAY_logo.jpg` and `LTPANEL.png` don't need to be deployed.

## Before going live

- Canonical URLs, Open Graph tags, JSON-LD and `sitemap.xml` use `https://dheerajtrivedi.github.io/Indway/`. If the site moves to a custom domain, find and replace that base URL across all these files.
- The specifications on the panel pages are typical values; check them against what the factory actually builds.

