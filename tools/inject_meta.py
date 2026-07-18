#!/usr/bin/env python3
"""
Inject Open Graph and Twitter meta tags into index.html from listing.json.

Bots like WhatsApp/Twitter often don't run JS, so we set static tags at build time.

Usage:
  python3 tools/inject_meta.py \
    [--listing data/listing.json] [--index index.html] [--base https://user.github.io/repo/]

Notes:
- --base should be the absolute site origin (and path) ending with '/'.
- If listing.cover is relative, it will be prefixed with --base.
- If listing.cover is absolute (starts with http), it will be used as-is.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from typing import Optional


def load_json(path: str) -> dict:
  with open(path, 'r', encoding='utf-8') as f:
    return json.load(f)


def read_text(path: str) -> str:
  with open(path, 'r', encoding='utf-8') as f:
    return f.read()


def write_text(path: str, content: str) -> None:
  with open(path, 'w', encoding='utf-8') as f:
    f.write(content)


def absolutize(url: str, base: Optional[str]) -> str:
  if not url:
    return url
  if url.startswith('http://') or url.startswith('https://'):
    return url
  if not base:
    return url
  return base.rstrip('/') + '/' + url.lstrip('/')


def escape_attr(value: str) -> str:
  """Escape a string for safe use inside a double-quoted HTML attribute."""
  return html.escape(value, quote=True)


def replace_meta_content(html_doc: str, *, prop: Optional[str] = None, name: Optional[str] = None, value: str) -> str:
  # Build a regex that matches the meta tag (by property or name) and replaces/sets content="value"
  if not (prop or name):
    return html_doc
  # Escape so quotes/angle brackets in the copy can't break out of the attribute.
  value = escape_attr(value)
  if prop:
    selector = rf"(\<meta[^>]*?property=[\"']{re.escape(prop)}[\"'][^>]*?)(/?>)"
  else:
    selector = rf"(\<meta[^>]*?name=[\"']{re.escape(name)}[\"'][^>]*?)(/?>)"

  def _inject(m: re.Match) -> str:
    tag_start, tag_end = m.group(1), m.group(2)
    # If content exists, replace it; else insert before tag_end
    if re.search(r"\bcontent=", tag_start, flags=re.IGNORECASE):
      tag_start = re.sub(r"content=([\"']).*?\1", lambda mm: f"content={mm.group(1)}{value}{mm.group(1)}", tag_start, flags=re.IGNORECASE)
    else:
      tag_start = tag_start.rstrip() + f" content=\"{value}\""
    return tag_start + tag_end

  return re.sub(selector, _inject, html_doc, count=1, flags=re.IGNORECASE|re.DOTALL)


def main() -> int:
  ap = argparse.ArgumentParser(description='Inject OG/Twitter meta from listing.json into index.html')
  ap.add_argument('--listing', default='data/listing.json')
  ap.add_argument('--index', default='index.html')
  ap.add_argument('--base', default=None, help='Absolute base URL for the site, ending with / (e.g., https://user.github.io/repo/)')
  args = ap.parse_args()

  listing = load_json(args.listing)
  html = read_text(args.index)

  title = listing.get('title') or 'Listing'
  summary = listing.get('summary') or listing.get('description') or ''
  cover = listing.get('cover') or (listing.get('images') or [None])[0] or ''
  og_image = absolutize(cover, args.base)
  og_url = args.base.rstrip('/') + '/' if args.base else ''

  # Inject OG
  html = replace_meta_content(html, prop='og:title', value=title)
  html = replace_meta_content(html, prop='og:description', value=summary)
  if og_image:
    html = replace_meta_content(html, prop='og:image', value=og_image)
  if og_url:
    html = replace_meta_content(html, prop='og:url', value=og_url)

  # Inject Twitter
  html = replace_meta_content(html, name='twitter:title', value=title)
  html = replace_meta_content(html, name='twitter:description', value=summary)
  if og_image:
    html = replace_meta_content(html, name='twitter:image', value=og_image)

  write_text(args.index, html)
  print('Injected meta tags into', args.index)
  if args.base:
    print('  base:', args.base)
  print('  title:', title)
  print('  image:', og_image or '(none)')
  return 0


if __name__ == '__main__':
  raise SystemExit(main())



