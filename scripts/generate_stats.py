#!/usr/bin/env python3
"""
ApplianceDB statistics page generator (`ApplianceDB-public`).

Reads the FULL private corpus (the private pipeline's appliancedb.sqlite) and writes a
citable, embeddable statistics page:

    stats/index.html          the page (URL /stats/)
    stats/charts/<slug>.svg   one standalone SVG per chart (for <img> embeds elsewhere)
    stats/data.json           every figure on the page, machine-readable

Only aggregates are written -- no row-level data (the repair titles quoted are catalogue
labels repeated across codes). Every figure states its denominator. Deliberately left out:
parts prices (only 17 priced parts / 20 procedures with a cost) and labor minutes (never
populated) -- too few observations to summarise honestly.

Re-run after each corpus refresh, then the private `tools/generate_landing.py` (which lists
/stats/ in the sitemap) or insert the entry by hand, then `python scripts/i18n_common.py build`
and `... check`.

Usage:
    python scripts/generate_stats.py                 # ../../09_Home_Appliances_ApplianceDB/appliancedb.sqlite
    python scripts/generate_stats.py --db PATH       # or APPLIANCEDB_SQLITE=PATH
"""
import argparse
import datetime as dt
import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_common import (Site, esc, n, pct, data, svg_hbar, figure, table, section, toc, tiles,  # noqa: E402
                          article_ld, COPY_JS, STATS_CSS, write_outputs)

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "stats"
FIRST_PUBLISHED = "2026-09-18"
DEFAULT_DB = BASE_DIR.parent / "09_Home_Appliances_ApplianceDB" / "appliancedb.sqlite"

SITE = Site(base_url="https://appliancedb.dataengineered.io", brand="ApplianceDB",
            snippet_label="ApplianceDB appliance error code statistics",
            surface="#ffffff", surface2="#f7f8fa", ink="#12151b", muted="#5a6472", grid="#e6e9ef", accent="#0a7c66",
            font="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            mono="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace")

TYPE_LABEL = {"washer": "Washer", "dishwasher": "Dishwasher", "oven_range": "Oven / range", "dryer": "Dryer", "refrigerator": "Refrigerator"}
SEVERITY_LABEL = {"stop_failure": "Stop failure", "degraded": "Degraded", "informational": "Informational"}
SEVERITY_ORDER = ["stop_failure", "degraded", "informational"]
DIFF_LABEL = {"easy": "Easy", "moderate": "Moderate", "advanced": "Advanced", "professional_only": "Professional only"}
DIFF_ORDER = ["easy", "moderate", "advanced", "professional_only"]
SOURCE_LABEL = {"manufacturer_listing": "manufacturer listing", "aggregator_listing": "repair-reference listing", "parts_catalog": "parts catalogue"}


def cat(key):
    return key.replace("_", " ")


def tlabel(t):
    return TYPE_LABEL.get(t, cat(t))


# ---------------------------------------------------------------------------
# statistics
# ---------------------------------------------------------------------------

def compute(db_path):
    con = sqlite3.connect(str(db_path))

    def q(sql, *a):
        return con.execute(sql, a).fetchall()

    s = {}
    s["snapshot_date"] = q("select max(substr(retrieved_at,1,10)) from data_sources")[0][0]
    s["codes"] = q("select count(*) from error_codes")[0][0]
    s["brands"] = q("select count(distinct brand_id) from error_codes")[0][0]
    s["markets"] = q("select count(distinct market) from error_codes")[0][0]
    s["types"] = q("select count(distinct appliance_type) from error_codes")[0][0]
    s["pairs"] = q("select count(*) from (select distinct brand_id, market, appliance_type from error_codes)")[0][0]
    s["procedures"] = q("select count(*) from repair_procedures")[0][0]
    s["codes_with_procedure"] = q("select count(distinct code_id) from repair_procedures")[0][0]
    s["categories"] = q("select count(distinct cause_category) from error_codes")[0][0]
    s["components"] = q("select count(distinct component) from error_codes")[0][0]
    s["sources"] = q("select count(distinct source_id) from error_codes")[0][0]

    # 1. brands
    s["by_brand"] = [dict(brand=b, codes=c, share_pct=pct(c, s["codes"]), markets=m.replace(",", ", "), types=t, source=", ".join(sorted({SOURCE_LABEL.get(x, x) for x in st.split(",")})),
                          with_procedure=w, with_procedure_pct=pct(w, c))
                     for b, c, m, t, st, w in q(
                         "select b.name, count(*) c, group_concat(distinct e.market), count(distinct e.appliance_type), group_concat(distinct s.source_type), "
                         "sum(case when exists(select 1 from repair_procedures r where r.code_id=e.code_id) then 1 else 0 end) "
                         "from error_codes e join brands b using(brand_id) join data_sources s using(source_id) group by b.name order by c desc, b.name")]
    s["by_market"] = [(m, c, pct(c, s["codes"])) for m, c in q("select market, count(*) from error_codes group by 1 order by 2 desc")]
    src = dict(q("select s.source_type, count(*) from error_codes e join data_sources s using(source_id) group by 1"))
    s["by_source"] = [(SOURCE_LABEL.get(k, k), v, pct(v, s["codes"])) for k, v in sorted(src.items(), key=lambda t: -t[1])]

    # 2. appliance types and the brand x type grid
    s["by_type"] = [(t, c, pct(c, s["codes"])) for t, c in q("select appliance_type, count(*) from error_codes group by 1 order by 2 desc")]
    types = [t for t, _, _ in s["by_type"]]
    grid = {}
    for b, m, t, c in q("select b.name, e.market, e.appliance_type, count(*) from error_codes e join brands b using(brand_id) group by 1,2,3"):
        grid.setdefault((b, m), {})[t] = c
    s["grid_types"] = types
    s["grid"] = [(b, m, {t: grid[(b, m)].get(t, 0) for t in types}, sum(grid[(b, m)].values()))
                 for (b, m) in sorted(grid, key=lambda k: (-sum(grid[k].values()), k))]
    s["pair_rows"] = [(f"{b} {m} {tlabel(t).lower()}", c) for b, m, t, c in q(
        "select b.name, e.market, e.appliance_type, count(*) c from error_codes e join brands b using(brand_id) group by 1,2,3 order by c desc, 1 limit 10")]

    # 3. cause categories
    s["by_cause"] = [(k, c, pct(c, s["codes"])) for k, c in q("select cause_category, count(*) from error_codes group by 1 order by 2 desc, 1")]
    lead = {}
    for t, k, c in q("select appliance_type, cause_category, count(*) from error_codes group by 1,2"):
        lead.setdefault(t, []).append((k, c))
    s["lead_by_type"] = []
    for t, c, p in s["by_type"]:
        rows = sorted(lead[t], key=lambda x: (-x[1], x[0]))
        top = rows[0][1]
        s["lead_by_type"].append((t, c, [k for k, v in rows if v == top], top, pct(top, c)))

    # 4. severity
    sev = dict(q("select severity, count(*) from error_codes where severity is not null group by 1"))
    s["severity_known"] = sum(sev.values())
    s["severity_unknown"] = s["codes"] - s["severity_known"]
    s["by_severity"] = [(k, sev.get(k, 0), pct(sev.get(k, 0), s["severity_known"])) for k in SEVERITY_ORDER]
    st = {}
    for t, k, c in q("select appliance_type, severity, count(*) from error_codes where severity is not null group by 1,2"):
        st.setdefault(t, {})[k] = c
    s["severity_by_type"] = [(t, sum(st.get(t, {}).values()), {k: st.get(t, {}).get(k, 0) for k in SEVERITY_ORDER}) for t in types]
    sc = {}
    for k, sv, c in q("select cause_category, severity, count(*) from error_codes where severity is not null group by 1,2"):
        sc.setdefault(k, {})[sv] = c
    s["stop_by_cause"] = sorted([(k, sum(v.values()), v.get("stop_failure", 0), pct(v.get("stop_failure", 0), sum(v.values()))) for k, v in sc.items() if sum(v.values()) >= 10],
                                key=lambda x: (-x[3], x[0]))

    # 5. components
    s["by_component"] = [(k, c, pct(c, s["codes"])) for k, c in q("select component, count(*) from error_codes group by 1 order by 2 desc, 1 limit 12")]

    # 6. repairs
    s["codes_without_procedure"] = s["codes"] - s["codes_with_procedure"]
    s["without_by_type"] = [(t, c) for t, c in q(
        "select appliance_type, count(*) from error_codes e where not exists (select 1 from repair_procedures r where r.code_id=e.code_id) group by 1 order by 2 desc")]
    ppc = dict(q("select n, count(*) from (select code_id, count(*) n from repair_procedures group by 1) group by 1"))
    s["procedures_per_code"] = [(k, ppc[k], pct(ppc[k], s["codes_with_procedure"])) for k in sorted(ppc)]
    dall = dict(q("select diy_difficulty, count(*) from repair_procedures group by 1"))
    d1 = dict(q("select diy_difficulty, count(*) from repair_procedures where rank=1 group by 1"))
    s["difficulty_all"] = [(k, dall.get(k, 0), pct(dall.get(k, 0), s["procedures"])) for k in DIFF_ORDER]
    s["difficulty_rank1"] = [(k, d1.get(k, 0), pct(d1.get(k, 0), s["codes_with_procedure"])) for k in DIFF_ORDER]
    dt_ = {}
    for t, k, c in q("select e.appliance_type, r.diy_difficulty, count(*) from repair_procedures r join error_codes e using(code_id) where r.rank=1 group by 1,2"):
        dt_.setdefault(t, {})[k] = c
    s["rank1_by_type"] = [(t, sum(dt_.get(t, {}).values()), {k: dt_.get(t, {}).get(k, 0) for k in DIFF_ORDER}) for t in types]
    s["rank_basis"] = [(k, c, pct(c, s["procedures"])) for k, c in q("select rank_basis, count(*) from repair_procedures group by 1 order by 2 desc")]
    s["top_titles"] = [(t, c) for t, c in q("select title, count(*) c from repair_procedures group by 1 order by c desc, 1 limit 10")]
    s["service_only"] = q("select count(*) from repair_procedures where title='Request professional service'")[0][0]

    # excluded fields, reported as coverage only
    s["priced_procedures"] = q("select count(*) from repair_procedures where parts_cost_min is not null")[0][0]
    s["priced_parts"] = q("select count(*) from replacement_parts")[0][0]
    s["labor_minutes"] = q("select count(*) from repair_procedures where est_labor_minutes is not null")[0][0]
    con.close()
    return s


# ---------------------------------------------------------------------------
# page
# ---------------------------------------------------------------------------

CSS = """
    :root { --bg: #f7f8fa; --panel: #ffffff; --ink: #12151b; --muted: #5a6472; --line: #e6e9ef; --brand: #0a7c66;
            --bg-paper: var(--bg); --bg-paper-2: var(--panel); --text-ink: var(--ink); --text-muted: var(--muted); --rule-color: var(--line); --accent: var(--brand); --radius: 12px; }
    @media (prefers-color-scheme: dark) { :root { --bg: #0b0e13; --panel: #141922; --ink: #eef1f6; --muted: #9aa6b6; --line: #232a35; --brand: #2dd4bf; } }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--bg); color: var(--ink); font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    a { color: var(--brand); text-decoration: none; } a:hover { text-decoration: underline; }
    .wrap { max-width: 1000px; margin: 0 auto; padding: 0 20px; }
    header { border-bottom: 1px solid var(--line); padding: 14px 0; font-size: .9rem; }
    .crumb { color: var(--muted); }
    .stats-wrap { max-width: 1000px; margin: 0 auto; padding: 36px 20px 64px; }
    .stats-wrap h1 { font-size: clamp(1.9rem, 3.4vw, 2.6rem); line-height: 1.15; margin: 0 0 8px; letter-spacing: -.01em; }
    .stats-wrap h2 { font-size: 1.45rem; margin: 0; }
    .stats-wrap h3 { font-size: 1.05rem; margin: 24px 0 0; }
    .stats-wrap .lede { font-size: 1.05rem; margin-top: 12px; max-width: 76ch; color: var(--muted); }
    .eyebrow { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--brand); font-weight: 600; margin-bottom: 8px; }
    figure { background: var(--panel); }
    .cta-inline { margin-top: 56px; padding: 24px; border: 1px solid var(--brand); border-radius: var(--radius); background: var(--panel); }
    .cta-inline p { color: var(--muted); margin: 8px 0 16px; }
    .btn { display: inline-block; padding: 10px 18px; border-radius: 999px; font-weight: 600; background: var(--brand); color: #fff; }
    .btn:hover { text-decoration: none; opacity: .92; }
    footer { border-top: 1px solid var(--line); margin-top: 36px; padding: 22px 0; color: var(--muted); font-size: .85rem; }
"""


def build_page(s, charts):
    site = SITE
    snap = s["snapshot_date"]
    src_note = f"Source: ApplianceDB, appliancedb.dataengineered.io/stats · snapshot {snap} · CC BY 4.0"
    sections = []

    # 1. brands
    bb = s["by_brand"]
    charts["codes-by-brand"] = svg_hbar(site, "Verified error codes per brand", f"{n(s['codes'])} codes across {n(s['brands'])} brands and {n(s['markets'])} markets",
                                        [(r["brand"], r["codes"], f"{n(r['codes'])} ({r['share_pct']}%)") for r in bb], src_note, label_w=120)
    ms = s["by_market"]
    sections.append(section(
        site, "brands", "Error codes per brand",
        f"{data(bb[0]['brand'])} has the most verified codes in the corpus with <strong>{n(bb[0]['codes'])} ({bb[0]['share_pct']}%)</strong>, the only brand covered in both markets, followed by {data(bb[1]['brand'])} ({n(bb[1]['codes'])}) and {data(bb[2]['brand'])} ({n(bb[2]['codes'])}). "
        f"{n(ms[0][1])} codes ({ms[0][2]}%) are {data(ms[0][0])}-market and {n(ms[1][1])} ({ms[1][2]}%) {data(ms[1][0])}-market; {s['by_source'][0][2]}% of all codes were derived from a {s['by_source'][0][0]}, the rest from a {s['by_source'][1][0]}.",
        figure(site, "codes-by-brand", charts["codes-by-brand"], "Verified error codes per brand", f"{n(s['codes'])} codes, {n(s['brands'])} brands"),
        table(["Brand", "Codes", "Share", "Markets", "Appliance types", "Source tier", "Codes with a ranked repair"],
              [(r["brand"], n(r["codes"]), f"{r['share_pct']}%", r["markets"], n(r["types"]), r["source"], f"{n(r['with_procedure'])} ({r['with_procedure_pct']}%)") for r in bb], {1, 2, 4, 6}),
        f"One row per error code, unique on (brand, market, appliance type, code): the same code string in the US and UK lists is two records. "
        f"Every code was re-derived from one of {n(s['sources'])} fetched source listings (a manufacturer support page or a disclosed repair reference); codes whose source stated no meaning were dropped, and brand pairs under 10 verified codes were dropped rather than padded."))

    # 2. appliance types
    bt = s["by_type"]
    charts["codes-by-appliance-type"] = svg_hbar(site, "Verified error codes per appliance type", f"{n(s['codes'])} codes, {n(s['types'])} appliance types",
                                                 [(tlabel(t), c, f"{n(c)} ({p}%)") for t, c, p in bt], src_note, label_w=120)
    pr = s["pair_rows"]
    sections.append(section(
        site, "appliance-types", "Error codes per appliance type",
        f"<strong>{tlabel(bt[0][0])}s account for {bt[0][2]}%</strong> of the corpus ({n(bt[0][1])} codes), followed by {tlabel(bt[1][0]).lower()}s ({n(bt[1][1])}, {bt[1][2]}%) and {tlabel(bt[2][0]).lower()}s ({n(bt[2][1])}, {bt[2][2]}%). "
        f"The {n(s['pairs'])} brand-market-type pairs range from {n(pr[0][1])} codes ({data(pr[0][0])}) down to 10, the inclusion floor.",
        figure(site, "codes-by-appliance-type", charts["codes-by-appliance-type"], "Verified error codes per appliance type", f"{n(s['codes'])} codes"),
        table(["Brand", "Market"] + [tlabel(t) for t in s["grid_types"]] + ["Total"],
              [(b, m) + tuple(n(g[t]) if g[t] else "–" for t in s["grid_types"]) + (n(tot),) for b, m, g, tot in s["grid"]], set(range(2, len(s["grid_types"]) + 3))),
        f"Coverage follows what each brand publishes per market and appliance type; a dash means the pair is not in the corpus, not that the brand has no such codes. "
        f"Denominator for every share: {n(s['codes'])} codes."))

    # 3. cause categories
    bc = s["by_cause"]
    charts["cause-categories"] = svg_hbar(site, "Error codes by fault category", f"{n(s['codes'])} codes, {n(s['categories'])} categories",
                                          [(cat(k), c, f"{n(c)} ({p}%)") for k, c, p in bc[:15]], src_note, label_w=130)
    lt = s["lead_by_type"]
    sections.append(section(
        site, "fault-categories", "The most common fault categories",
        f"The largest fault category is <strong>{data(cat(bc[0][0]))}</strong>, {n(bc[0][1])} of {n(s['codes'])} codes ({bc[0][2]}%), followed by {data(cat(bc[1][0]))} ({n(bc[1][1])}, {bc[1][2]}%) and {data(cat(bc[2][0]))} ({n(bc[2][1])}, {bc[2][2]}%). "
        f"The leading category differs by appliance: {'; '.join(f'{tlabel(t).lower()}s {data(cat(k[0])) if len(k) == 1 else data(cat(k[0])) + str(chr(32)) + str(chr(47)) + str(chr(32)) + data(cat(k[1]))} ({n(top)} of {n(c)})' for t, c, k, top, p in lt)}.",
        figure(site, "cause-categories", charts["cause-categories"], "Error codes by fault category", f"top 15 of {n(s['categories'])} categories"),
        table(["Fault category", "Codes", "Share"], [(cat(k), n(c), f"{p}%") for k, c, p in bc], {1, 2})
        + "<h3>Leading category per appliance type</h3>"
        + table(["Appliance type", "Codes", "Leading category", "Codes in it", "Share of the type"],
                [(tlabel(t), n(c), " / ".join(cat(x) for x in k), n(top), f"{p}%") for t, c, k, top, p in lt], {1, 3, 4}),
        f"cause_category is a controlled label assigned per code from the source's stated meaning ({n(s['categories'])} values); each code carries exactly one. "
        f"Two categories are shown where they tie for first place. Categories describe what the code reports, not the confirmed root cause."))

    # 4. severity
    bs = s["by_severity"]
    charts["severity"] = svg_hbar(site, "Error codes by severity", f"{n(s['severity_known'])} codes with a severity class",
                                  [(SEVERITY_LABEL[k], c, f"{n(c)} ({p}%)") for k, c, p in bs], src_note, label_w=120)
    sbc = s["stop_by_cause"]
    sections.append(section(
        site, "severity", "How many codes stop the appliance",
        f"Of the {n(s['severity_known'])} codes with a severity class, <strong>{bs[0][2]}%</strong> are {data('stop failure')} (the appliance halts until the fault clears), {bs[1][2]}% {data('degraded')} and {bs[2][2]}% {data('informational')}. "
        f"{n(s['severity_unknown'])} codes carry no severity and are excluded. Among categories with at least 10 classified codes, {data(cat(sbc[0][0]))} has the highest stop-failure share ({sbc[0][3]}%) and {data(cat(sbc[-1][0]))} the lowest ({sbc[-1][3]}%).",
        figure(site, "severity", charts["severity"], "Error codes by severity", f"{n(s['severity_known'])} classified codes"),
        table(["Appliance type", "Classified codes"] + [SEVERITY_LABEL[k] for k in SEVERITY_ORDER],
              [(tlabel(t), n(c)) + tuple(f"{n(d[k])} ({pct(d[k], c)}%)" for k in SEVERITY_ORDER) for t, c, d in s["severity_by_type"]], {1, 2, 3, 4})
        + "<h3>Stop-failure share by fault category</h3>"
        + table(["Fault category", "Classified codes", "Stop failure", "Share"], [(cat(k), n(c), n(sf), f"{p}%") for k, c, sf, p in sbc], {1, 2, 3}),
        "severity is assigned from the source's description of the appliance's behaviour when the code shows: stop failure, degraded operation or an informational message. "
        "Categories with fewer than 10 classified codes are left out of the share table."))

    # 5. components
    bcp = s["by_component"]
    charts["components"] = svg_hbar(site, "Components most often named by error codes", f"Top 12 of {n(s['components'])} components, {n(s['codes'])} codes",
                                    [(k, c, f"{n(c)} ({p}%)") for k, c, p in bcp], src_note, label_w=150)
    sections.append(section(
        site, "components", "Which components the codes point to",
        f"The <strong>{data(bcp[0][0])}</strong> is the component most often named, by {n(bcp[0][1])} codes ({bcp[0][2]}%), ahead of the {data(bcp[1][0])} ({n(bcp[1][1])}) and the {data(bcp[2][0])} ({n(bcp[2][1])}). "
        f"{n(s['components'])} distinct components are named across the corpus.",
        figure(site, "components", charts["components"], "Components most often named by error codes", f"top 12 of {n(s['components'])} components"),
        table(["Component", "Codes", "Share"], [(k, n(c), f"{p}%") for k, c, p in bcp], {1, 2}),
        "component is the part the source names as the subject of the code, normalised to one label per code; it is where diagnosis starts, not a confirmed failed part."))

    # 6. repairs
    da, d1 = s["difficulty_all"], s["difficulty_rank1"]
    charts["repair-difficulty"] = svg_hbar(site, "DIY difficulty of the ranked repair procedures", f"{n(s['procedures'])} procedures for {n(s['codes_with_procedure'])} codes",
                                           [(DIFF_LABEL[k], c, f"{n(c)} ({p}%)") for k, c, p in da], src_note, label_w=140)
    easy1 = next(p for k, c, p in d1 if k == "easy")
    pro1 = next(p for k, c, p in d1 if k == "professional_only")
    wbt = s["without_by_type"]
    rb = s["rank_basis"]
    sections.append(section(
        site, "repairs", "How much of the repair work is DIY",
        f"<strong>{n(s['codes_with_procedure'])} of {n(s['codes'])} codes ({pct(s['codes_with_procedure'], s['codes'])}%)</strong> carry at least one ranked repair procedure, {n(s['procedures'])} in all. "
        f"{da[0][2]}% of procedures are {data('easy')} and {da[3][2]}% {data('professional only')}; looking at the first-ranked procedure per code, {easy1}% are easy and {pro1}% professional only. "
        f"{n(s['service_only'])} procedures consist of requesting professional service. The other {n(s['codes_without_procedure'])} codes ({', '.join(f'{n(c)} {tlabel(t).lower()}' for t, c in wbt)}) come from sources that state no repair and carry none.",
        figure(site, "repair-difficulty", charts["repair-difficulty"], "DIY difficulty of the ranked repair procedures", f"{n(s['procedures'])} procedures"),
        table(["Appliance type", "Codes with a repair"] + [DIFF_LABEL[k] for k in DIFF_ORDER],
              [(tlabel(t), n(c)) + tuple(f"{n(d[k])} ({pct(d[k], c)}%)" for k in DIFF_ORDER) for t, c, d in s["rank1_by_type"]], {1, 2, 3, 4, 5})
        + "<h3>Most frequent procedure titles</h3>"
        + table(["Procedure", "Codes"], [(t, n(c)) for t, c in s["top_titles"]], {1}),
        f"Procedures are ranked per code with a stated basis: {', '.join(f'{n(c)} {cat(k)} ({p}%)' for k, c, p in rb)}; a rank without evidence never ships. "
        f"diy_difficulty is assigned per procedure (easy, moderate, advanced, professional only). The first-ranked table counts rank-1 procedures by the appliance type of their code."))

    contents = toc([("brands", "Codes per brand"), ("appliance-types", "Codes per appliance type"), ("fault-categories", "Fault categories"),
                    ("severity", "Severity"), ("components", "Components named"), ("repairs", "Repair difficulty"), ("method", "Method, reuse and citation")])
    tile_html = tiles([("Verified codes", n(s["codes"])), ("Brands", n(s["brands"])), ("Markets", n(s["markets"])), ("Brand-market-type pairs", n(s["pairs"])),
                       ("Ranked repairs", n(s["procedures"])), ("Snapshot", snap)])
    title_tag = f"Appliance Error Code Statistics {snap[:4]} — Codes per Brand and Type, Fault Categories, Severity | ApplianceDB"
    desc = (f"Home appliance error codes in numbers: {n(s['codes'])} verified codes across {n(s['brands'])} brands, {n(s['markets'])} markets and {n(s['types'])} appliance types. Codes per brand and appliance type, "
            f"fault categories ({cat(bc[0][0])} leads at {bc[0][2]}%), severity, components named, DIY share of ranked repairs. Free to cite and embed.")
    ld = article_ld(site, "Home appliance error codes in numbers: statistics from the ApplianceDB corpus", desc, FIRST_PUBLISHED,
                    f"{site.base_url}/assets/kaggle-cover.png", ["appliance error codes", "appliance repair", "washer error codes", "field service", "home warranty"])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title_tag)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{site.page_url}">
<link rel="alternate" hreflang="en" href="{site.page_url}">
<meta property="og:title" content="Appliance error codes in numbers — ApplianceDB statistics {snap[:4]}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{site.page_url}">
<meta property="og:image" content="{site.base_url}/assets/kaggle-cover.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0a7c66">
<link rel="manifest" href="/site.webmanifest">
{ld}
<style>{CSS}{STATS_CSS}</style>
</head>
<body>
<header><div class="wrap crumb">
  <a href="/">ApplianceDB</a> › <span>Statistics</span>
</div></header>
<main class="stats-wrap">
  <p class="eyebrow">Corpus statistics · snapshot {esc(snap)}</p>
  <h1>Home appliance error codes in numbers</h1>
  <p class="lede">Aggregate statistics computed from the full ApplianceDB corpus: {n(s['codes'])} verified error codes keyed by brand, market, appliance type and code across {n(s['brands'])} brands, mapped to {n(s['procedures'])} ranked repair procedures, every fact traced to a fetched source listing. Every figure states its denominator and is free to cite, quote and embed with a link to this page.</p>
  <ul class="tiles">{tile_html}</ul>
  <nav class="toc" aria-label="Contents"><strong>On this page</strong><ol>{contents}</ol></nav>

{"".join(sections)}

  <section class="stat" id="method">
    <h2>Method, reuse and citation</h2>
    <ul class="method">
      <li><strong>Source.</strong> The full ApplianceDB corpus retrieved {snap}: {n(s['codes'])} codes and {n(s['procedures'])} procedures, each re-derived from one of {n(s['sources'])} fetched manufacturer support pages or disclosed repair references, never from model memory; meanings and steps are original paraphrase. Every row keeps its source tier and URL; see <a href="/SOURCES.md">Sources</a> and the <a href="/DATA_DICTIONARY.md">data dictionary</a>.</li>
      <li><strong>Nothing is padded.</strong> Codes whose source states no meaning were dropped, brand pairs under 10 verified codes were dropped, codes whose source lists no repair carry none, and codes without a severity class are excluded from the severity shares. Each section states its denominator.</li>
      <li><strong>Left out on purpose.</strong> Parts prices ({n(s['priced_parts'])} priced OEM parts, {n(s['priced_procedures'])} procedures with a cost) and labor minutes ({n(s['labor_minutes'])} populated) are too few to summarise; they stay row-level fields in the dataset.</li>
      <li><strong>Refresh.</strong> ApplianceDB is curated; this page and its charts are regenerated with each corpus edition, so figures move. Cite the snapshot date.</li>
      <li><strong>Reuse.</strong> The figures and charts on this page are published under <a href="https://creativecommons.org/licenses/by/4.0/" rel="license">CC BY 4.0</a>: use them in articles, decks and product pages with a link to <span translate="no">{site.page_url}</span>. The machine-readable version is <a href="/stats/data.json">data.json</a>. The row-level corpus is in the <a href="https://github.com/ApplianceDB/ApplianceDB-public">public repository</a> under ODbL; the <a href="/#pricing">commercial licence</a> and the <a href="/enterprise">enterprise integration licence</a> cover embedding it in products.</li>
      <li><strong>Suggested citation.</strong> <span translate="no">ApplianceDB ({snap[:4]}). <em>Home appliance error codes in numbers</em>, snapshot {snap}. DataEngineered. {site.page_url}</span></li>
      <li><strong>Questions or corrections:</strong> <a href="/#contact">contact form</a> or appliancedb@dataengineered.io.</li>
    </ul>
  </section>

  <div class="cta-inline">
    <h3 style="margin:0">Need this corpus inside a warranty or field-service product?</h3>
    <p>Every code with its ranked repairs, difficulty, OEM parts and per-row provenance, as CSV, Parquet and SQLite, with embedding rights and priority coverage requests.</p>
    <a class="btn" href="/enterprise">Enterprise integration licence</a>
  </div>
</main>
<footer><div class="wrap">ApplianceDB · Data ODbL-1.0 · <a href="/" translate="no">appliancedb</a><div class="catalog-line" style="text-align:center; margin-top:14px; font-size:0.85rem; opacity:0.85;"><a href="https://dataengineered.io/">Part of the DataEngineered catalog &rarr;</a> &middot; <a href="https://dataengineered.io/about">About</a> &middot; <a href="https://dataengineered.io/terms">Terms</a> &middot; <a href="https://dataengineered.io/privacy">Privacy</a> &middot; <a href="https://dataengineered.io/refund-policy">Refund policy</a></div></div></footer>
{COPY_JS}
</body>
</html>
"""


def build_data_json(s):
    return {
        "dataset": SITE.brand, "page": SITE.page_url, "generated": dt.date.today().isoformat(), "snapshot": s["snapshot_date"],
        "license": "CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) - attribute with a link to the page",
        "totals": {k: s[k] for k in ("codes", "brands", "markets", "types", "pairs", "procedures", "codes_with_procedure", "categories", "components", "sources")},
        "by_brand": s["by_brand"],
        "by_market": [dict(market=m, codes=c, share_pct=p) for m, c, p in s["by_market"]],
        "by_source_tier": [dict(tier=k, codes=c, share_pct=p) for k, c, p in s["by_source"]],
        "by_appliance_type": [dict(type=t, codes=c, share_pct=p) for t, c, p in s["by_type"]],
        "brand_market_type_grid": [dict(brand=b, market=m, total=tot, **g) for b, m, g, tot in s["grid"]],
        "fault_categories": {"all": [dict(category=k, codes=c, share_pct=p) for k, c, p in s["by_cause"]],
                             "leading_by_type": [dict(type=t, codes=c, leading=k, codes_in_leading=top, share_pct=p) for t, c, k, top, p in s["lead_by_type"]]},
        "severity": {"classified": s["severity_known"], "unclassified": s["severity_unknown"],
                     "all": [dict(severity=k, codes=c, share_pct=p) for k, c, p in s["by_severity"]],
                     "by_type": [dict(type=t, classified=c, **d) for t, c, d in s["severity_by_type"]],
                     "stop_failure_by_category": [dict(category=k, classified=c, stop_failure=sf, share_pct=p) for k, c, sf, p in s["stop_by_cause"]]},
        "components": [dict(component=k, codes=c, share_pct=p) for k, c, p in s["by_component"]],
        "repairs": {"procedures": s["procedures"], "codes_with_procedure": s["codes_with_procedure"], "codes_without_procedure": s["codes_without_procedure"],
                    "without_by_type": [dict(type=t, codes=c) for t, c in s["without_by_type"]],
                    "procedures_per_code": [dict(procedures=k, codes=c, share_pct=p) for k, c, p in s["procedures_per_code"]],
                    "difficulty_all": [dict(level=k, procedures=c, share_pct=p) for k, c, p in s["difficulty_all"]],
                    "difficulty_rank1": [dict(level=k, codes=c, share_pct=p) for k, c, p in s["difficulty_rank1"]],
                    "rank1_by_type": [dict(type=t, codes=c, **d) for t, c, d in s["rank1_by_type"]],
                    "rank_basis": [dict(basis=k, procedures=c, share_pct=p) for k, c, p in s["rank_basis"]],
                    "top_titles": [dict(title=t, codes=c) for t, c in s["top_titles"]], "request_professional_service": s["service_only"]},
        "excluded": {"priced_parts": s["priced_parts"], "procedures_with_cost": s["priced_procedures"], "procedures_with_labor_minutes": s["labor_minutes"],
                     "reason": "too few observations to summarise; kept as row-level fields"},
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--db", default=os.environ.get("APPLIANCEDB_SQLITE", str(DEFAULT_DB)))
    args = ap.parse_args()
    db = Path(args.db)
    if not db.is_file():
        raise SystemExit(f"SQLite corpus not found: {db}")
    s = compute(db)
    charts = {}
    page = build_page(s, charts)
    write_outputs(OUT_DIR, page, charts, build_data_json(s))
    print(f"stats/index.html + {len(charts)} charts + data.json  (snapshot {s['snapshot_date']}, {s['codes']:,} codes)")


if __name__ == "__main__":
    main()
