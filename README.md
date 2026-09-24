# Indway

Marketing site for Indway, an LT panel manufacturer (PCC, MCC, APFC, distribution boards, AMF panels and feeder pillars).

The site is a single static page. Its hero is an interactive 3D model of an LT panel lineup, built with [three.js](https://threejs.org/), that visitors can explore through hotspots and a guided tour.

## Project structure

```
index.html          The whole site: markup, styles and the three.js scene
assets/
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

- The contact phone number in `index.html` is still a placeholder (`+91 00000 00000`).
