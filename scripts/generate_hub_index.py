#!/usr/bin/env python3
"""Regenerate the homepage "browse by appliance" block.

Every code page under landing/ is reachable only through its appliance-type
hub (landing/washer, landing/dryer, ...). Those hubs each list their own
children, but the homepage linked just one of them, so four of the five
hubs -- and the 188 code pages beneath them -- were orphaned: reachable in
the sitemap but not by following links from the homepage.

This writes the block between the BEGIN/END markers in index.html, deriving
both the hub list and the per-type counts from what is actually on disk, so
the counts cannot drift from the pages.

Run from the repo root:  python scripts/generate_hub_index.py
"""

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANDING = ROOT / "landing"
INDEX = ROOT / "index.html"

BEGIN = "<!-- BEGIN:hub-browse -->"
END = "<!-- END:hub-browse -->"

# Appliance types, in the order the coverage table above presents them.
# Key is the hub slug (landing/<slug>); value is its display name.
TYPES = [
    ("washer", "Washer"),
    ("dryer", "Dryer"),
    ("dishwasher", "Dishwasher"),
    ("refrigerator", "Refrigerator"),
    ("oven-range", "Oven / Range"),
]


def code_counts():
    """Count code pages per appliance type from the filenames on disk.

    A code page is named <brand>[-<market>]-<type>-<code>.html, and <type>
    may itself contain a hyphen (oven-range), so match the known types
    directly rather than splitting on the separator.
    """
    counts = Counter()
    hub_slugs = {slug for slug, _ in TYPES}
    for page in LANDING.glob("*.html"):
        stem = page.stem
        if stem in hub_slugs:
            continue  # the hub itself, not a code page
        for slug, _ in TYPES:
            if f"-{slug}-" in stem:
                counts[slug] += 1
                break
    return counts


def build_block(counts):
    cards = []
    for slug, label in TYPES:
        n = counts.get(slug, 0)
        if not n:
            continue  # never advertise a hub with nothing behind it
        cards.append(
            '      <a class="hubcard" href="/landing/{slug}">'
            '<span class="hubcard-n">{n}</span>'
            '<span class="hubcard-l">{label} codes</span></a>'.format(
                slug=slug, label=label, n=n
            )
        )
    total = sum(counts.get(slug, 0) for slug, _ in TYPES)
    return (
        "{begin}\n"
        '  <section id="browse">\n'
        "    <h2>Browse the code pages</h2>\n"
        "    <p>Every one of the {total} verified codes has its own page with the meaning, "
        "the implicated component, ranked repair steps and the source it was derived from. "
        "Pick an appliance to see its full list.</p>\n"
        '    <div class="hubgrid">\n'
        "{cards}\n"
        "    </div>\n"
        '    <p class="note">The code pages are free to read. The paid snapshot is the same '
        "data as structured CSV and SQLite, with the ranked repairs, OEM part numbers and "
        "dated price observations joined per row.</p>\n"
        "  </section>\n"
        "  {end}"
    ).format(begin=BEGIN, end=END, total=total, cards="\n".join(cards))


def main():
    if not INDEX.is_file():
        sys.exit("index.html not found -- run this from the repo root")

    counts = code_counts()
    if not counts:
        sys.exit("no code pages found under landing/ -- refusing to write an empty block")

    html = INDEX.read_text(encoding="utf-8")
    block = build_block(counts)

    if BEGIN in html and END in html:
        html = re.sub(
            re.escape(BEGIN) + r".*?" + re.escape(END),
            lambda _: block,
            html,
            flags=re.DOTALL,
        )
    else:
        # First run: place the block immediately after the coverage section.
        anchor = "</section>\n\n<section id=\"integrity\">"
        if anchor not in html:
            sys.exit("could not find the insertion point after #coverage")
        html = html.replace(anchor, "</section>\n\n" + block + "\n\n<section id=\"integrity\">", 1)

    INDEX.write_text(html, encoding="utf-8", newline="")

    total = sum(counts.values())
    print("wrote browse block: %d hubs, %d code pages" % (len(counts), total))
    for slug, label in TYPES:
        print("  %-14s %4d" % (slug, counts.get(slug, 0)))


if __name__ == "__main__":
    main()
