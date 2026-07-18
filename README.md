# Tern Link A7 - For Sale

Mobile-friendly, shareable landing page to sell a Tern Link A7. Includes WhatsApp CTA and social previews.

Adapted from [tern-gsd-s10-lx-sale](https://github.com/yaffol/tern-gsd-s10-lx-sale).

## Quick start
1. Put your photos into `images/web/` (JPG/PNG/WebP), web-sized for speed.
2. Run the manifest generator to populate `cover` and `images`:
   - `python3 tools/generate_manifest.py`
3. Edit `data/listing.json` - replace every `TODO` with real copy (price, story, specs, good/bad points, extras).
4. Inject static OG/Twitter meta tags (for WhatsApp/Twitter previews):
   - Local preview: `python3 tools/inject_meta.py --base http://localhost:8000/`
   - After deploy: `python3 tools/inject_meta.py --base https://yaffol.github.io/tern-link-a7-sale/`
5. Serve locally: `python3 -m http.server` and open `http://localhost:8000`.

## Deploy (GitHub Pages)
- Push to `main`.
- GitHub → Settings → Pages: `Deploy from a branch`, branch `main`, folder `/ (root)`, Save.
- Publishes at `https://yaffol.github.io/tern-link-a7-sale/`.

## Tools

- `tools/generate_manifest.py`
  - Scans `images/web/` (if present) or `images/` and updates `data/listing.json` with `cover` and ordered `images`.
- `tools/inject_meta.py`
  - Writes absolute `og:*` and `twitter:*` tags directly into `index.html` from `data/listing.json`.
  - Re-run it whenever the cover photo or summary changes - WhatsApp doesn't run JS.

## License
MIT
