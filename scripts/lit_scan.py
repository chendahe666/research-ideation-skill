#!/usr/bin/env python3
"""Field scan for building a research "field map".

Pulls papers for one or more queries from OpenAlex (title+abstract match; OpenAlex
also indexes arXiv preprints, usually with a lag of days to weeks). Writes:
  <out>.md   - yearly publication trend per query, most-cited papers per era,
               newest papers (with abstract snippets)
  <out>.json - every record, full abstracts, for the LLM to read

Standard library only. Examples:
  python lit_scan.py -q "3D watermarking" -q "NeRF watermark" -q "Gaussian splatting watermark"
  python lit_scan.py -q "\"generative AI\" self-regulated learning" --from 2018 --eras 2018-2021,2022-2023,2024-2026
  python lit_scan.py -q "mesh watermarking" --top 25 --recent 30 --out mesh_wm

Optional env vars: OPENALEX_API_KEY (higher quota), OPENALEX_EMAIL (polite pool).
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

OPENALEX = "https://api.openalex.org/works"
UA = "research-ideation-skill/1.0 (lit_scan.py)"


def http_get(url, retries=5, timeout=40):
    delay = 2.0
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                retry_after = e.headers.get("Retry-After", "")
                time.sleep(min(60, int(retry_after)) if retry_after.isdigit() else delay)
                delay *= 2
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise


def openalex(params):
    params = dict(params)
    if os.environ.get("OPENALEX_API_KEY"):
        params["api_key"] = os.environ["OPENALEX_API_KEY"]
    if os.environ.get("OPENALEX_EMAIL"):
        params["mailto"] = os.environ["OPENALEX_EMAIL"]
    time.sleep(0.3)  # stay well under OpenAlex's per-second limit
    return json.loads(http_get(OPENALEX + "?" + urllib.parse.urlencode(params)))


def oa_filter(query, y0, y1):
    # Commas separate filters in OpenAlex, so they cannot appear inside the search text.
    q = query.replace(",", " ")
    return f"title_and_abstract.search:{q},publication_year:{y0}-{y1}"


def rebuild_abstract(inv):
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return re.sub(r"(\\n|\s)+", " ", " ".join(pos[i] for i in sorted(pos))).strip()


def oa_record(w):
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
    return {
        "source": "openalex",
        "id": w.get("id"),
        "doi": w.get("doi"),
        "title": (w.get("title") or "").strip(),
        "year": w.get("publication_year"),
        "date": w.get("publication_date"),
        "cited_by": w.get("cited_by_count", 0),
        "venue": src.get("display_name") or "",
        "url": w.get("doi") or loc.get("landing_page_url") or w.get("id"),
        "authors": [a["author"]["display_name"] for a in (w.get("authorships") or [])[:6]],
        "abstract": rebuild_abstract(w.get("abstract_inverted_index")),
    }


SELECT = "id,doi,title,publication_year,publication_date,cited_by_count,primary_location,authorships,abstract_inverted_index"


def trend(query, y0, y1):
    data = openalex({"filter": oa_filter(query, y0, y1), "group_by": "publication_year"})
    return {int(g["key"]): g["count"] for g in data.get("group_by", [])}


def top_cited(query, y0, y1, n):
    data = openalex({"filter": oa_filter(query, y0, y1), "sort": "cited_by_count:desc",
                     "per_page": n, "select": SELECT})
    return [oa_record(w) for w in data.get("results", [])]


def newest(query, y0, y1, n):
    data = openalex({"filter": oa_filter(query, y0, y1), "sort": "publication_date:desc",
                     "per_page": n, "select": SELECT})
    return [oa_record(w) for w in data.get("results", [])]


def default_eras(y0, y1):
    span = y1 - y0 + 1
    if span <= 4:
        return [(y0, y1)]
    # Older eras wider, recent eras narrower: the recent past is where gaps get filled.
    recent = (y1 - 1, y1)
    mid = (y1 - 3, y1 - 2)
    rest = (y0, y1 - 4)
    mid_split = (rest[0] + rest[1]) // 2
    eras = [(rest[0], mid_split), (mid_split + 1, rest[1]), mid, recent]
    return [e for e in eras if e[0] <= e[1]]


def snippet(text, n):
    text = text or ""
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + " ..."


def fmt_paper(i, p, n_abs):
    cites = f" · {p['cited_by']} cites" if p.get("cited_by") is not None else ""
    venue = f", {p['venue']}" if p.get("venue") else ""
    line = f"{i}. **{p['title']}** ({p.get('date') or p.get('year')}{venue}){cites} — {p['url']}"
    if p.get("abstract") and n_abs > 0:
        line += f"\n   > {snippet(p['abstract'], n_abs)}"
    return line


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-q", "--query", action="append", required=True,
                    help="search query; repeat to compare sub-directions. Quotes make phrases.")
    this_year = dt.date.today().year
    ap.add_argument("--from", dest="y0", type=int, default=this_year - 10)
    ap.add_argument("--to", dest="y1", type=int, default=this_year)
    ap.add_argument("--eras", help='e.g. "2015-2019,2020-2022,2023-2024,2025-2026"')
    ap.add_argument("--top", type=int, default=12, help="most-cited papers per era per query")
    ap.add_argument("--recent", type=int, default=15, help="newest papers per query (0 to skip)")
    ap.add_argument("--abs", type=int, default=350, help="abstract snippet length in the .md")
    ap.add_argument("--out", default="field_scan")
    args = ap.parse_args()

    if args.eras:
        eras = [tuple(int(x) for x in e.split("-")) for e in args.eras.split(",")]
    else:
        eras = default_eras(args.y0, args.y1)

    md = [f"# Field scan — generated {dt.date.today().isoformat()}", "",
          "Queries: " + "; ".join(f"`{q}`" for q in args.query), "",
          "Source: OpenAlex, title+abstract match. Counts are relative signals, not exact field sizes; "
          "citation counts favour older papers; the last few weeks of arXiv may be missing — "
          "check those by web search before claiming a gap is open.", ""]
    dump = {"generated": dt.date.today().isoformat(), "queries": {}}
    recent_from = args.y1 - 1

    # 1. Trend table
    trends = {}
    for q in args.query:
        try:
            trends[q] = trend(q, args.y0, args.y1)
        except Exception as e:  # keep going; report per query
            trends[q] = {}
            print(f"[warn] trend failed for {q!r}: {e}", file=sys.stderr)
    md += ["## 1. Publication trend per year", "",
           "| Year | " + " | ".join(args.query) + " |",
           "|---|" + "---|" * len(args.query)]
    for y in range(args.y0, args.y1 + 1):
        md.append(f"| {y} | " + " | ".join(str(trends[q].get(y, 0)) for q in args.query) + " |")
    md.append("")

    # 2. Most-cited per era, 3. newest arXiv
    for q in args.query:
        qd = {"trend": trends[q], "eras": {}, "newest": []}
        md += [f"## 2. Most-cited papers by era — `{q}`", ""]
        for y0, y1 in eras:
            try:
                papers = top_cited(q, y0, y1, args.top)
            except Exception as e:
                papers = []
                print(f"[warn] top-cited failed for {q!r} {y0}-{y1}: {e}", file=sys.stderr)
            qd["eras"][f"{y0}-{y1}"] = papers
            md += [f"### {y0}–{y1}", ""]
            md += [fmt_paper(i, p, args.abs) for i, p in enumerate(papers, 1)] or ["(no results)"]
            md.append("")
        if args.recent > 0:
            try:
                recent = newest(q, recent_from, args.y1, args.recent)
            except Exception as e:
                recent = []
                print(f"[warn] newest failed for {q!r}: {e}", file=sys.stderr)
            qd["newest"] = recent
            md += [f"## 3. Newest papers ({recent_from}–{args.y1}) — `{q}`", ""]
            md += [fmt_paper(i, p, args.abs) for i, p in enumerate(recent, 1)] or ["(no results)"]
            md.append("")
        dump["queries"][q] = qd

    with open(args.out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    with open(args.out + ".json", "w", encoding="utf-8") as f:
        json.dump(dump, f, ensure_ascii=False, indent=1)
    n = sum(len(v) for qd in dump["queries"].values() for v in qd["eras"].values()) + \
        sum(len(qd["newest"]) for qd in dump["queries"].values())
    print(f"wrote {args.out}.md and {args.out}.json ({n} paper records)")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
