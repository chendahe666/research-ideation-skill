#!/usr/bin/env python3
"""Mine public OpenReview reviews for recurring weaknesses in a sub-field.

1. Searches a venue (ICLR / NeurIPS / ICML / TMLR / COLM ... anything on OpenReview)
   for submissions matching a keyword — works without login.
2. Downloads official reviews, meta-reviews, decisions and author rebuttals for
   those submissions and writes them to markdown, plus a flat list of every
   "weaknesses / questions / limitations" field for clustering into gaps.

Step 2 needs an OpenReview login: OpenReview now answers anonymous review
requests with a human-verification challenge. Set your own account in env vars
before running (never paste the password into a chat):
  OPENREVIEW_USERNAME=you@example.com  OPENREVIEW_PASSWORD=...     or  OPENREVIEW_TOKEN=...
Without them, the script still writes the matched submissions and their forum
links so you can read the reviews in a browser.

Standard library only. Examples:
  python openreview_reviews.py -t watermark -v ICLR.cc/2025/Conference -v NeurIPS.cc/2024/Conference
  python openreview_reviews.py -t "gaussian splatting" -v ICLR.cc/2025/Conference --status rejected --max 15
  python openreview_reviews.py -t watermark --require "3d" -v ICLR.cc/2025/Conference -v NeurIPS.cc/2025/Conference
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api2.openreview.net"
UA = "research-ideation-skill/1.0 (openreview_reviews.py)"

# Fields worth reading, in display order; anything else long and textual is appended.
REVIEW_FIELDS = ["summary", "strengths", "weaknesses", "questions", "limitations",
                 "main_review", "review", "strengths_and_weaknesses", "summary_of_the_review",
                 "rating", "recommendation", "confidence", "soundness", "novelty", "contribution"]
GAP_FIELDS = {"weaknesses", "questions", "limitations", "strengths_and_weaknesses", "main_review", "review"}
SKIP_FIELDS = {"code_of_conduct", "code_of_ethics", "flag_for_ethics_review", "details_of_ethics_concerns",
               "first_time_reviewer", "title"}


class Challenge(Exception):
    pass


def call(method, path, params=None, body=None, token=None, retries=4):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    headers = {"User-Agent": UA, "Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    delay = 2.0
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8", errors="replace")
            if e.code == 403 and "Challenge" in text:
                raise Challenge(text[:300])
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise RuntimeError(f"HTTP {e.code} on {path}: {text[:300]}")


def login():
    if os.environ.get("OPENREVIEW_TOKEN"):
        return os.environ["OPENREVIEW_TOKEN"]
    user, pw = os.environ.get("OPENREVIEW_USERNAME"), os.environ.get("OPENREVIEW_PASSWORD")
    if not (user and pw):
        return None
    return call("POST", "/login", body={"id": user, "password": pw}).get("token")


def val(content, key):
    v = content.get(key)
    if isinstance(v, dict):
        v = v.get("value")
    if isinstance(v, list):
        v = ", ".join(str(x) for x in v)
    return "" if v is None else str(v)


def status_of(venue_str):
    s = venue_str.lower()
    if "withdrawn" in s:
        return "withdrawn"
    if "desk rejected" in s or "rejected" in s:
        return "rejected"
    if s.startswith("submitted to"):
        return "rejected-or-pending"
    return "accepted"


def search(term, venue, limit):
    notes, offset = [], 0
    while len(notes) < limit:
        page = call("GET", "/notes/search", {"term": term, "type": "terms", "content": "all",
                                             "source": "forum", "group": venue,
                                             "limit": min(100, limit - len(notes)), "offset": offset})
        batch = page.get("notes", [])
        if not batch:
            break
        notes += batch
        offset += len(batch)
        time.sleep(0.5)
    # the search is full-text; keep only notes that are actual submissions to this venue
    return [n for n in notes if n.get("id") == n.get("forum")][:limit]


def kind_of(note):
    inv = " ".join(note.get("invitations", []))
    for k in ("Official_Review", "Meta_Review", "Decision", "Rebuttal", "Official_Comment", "Public_Comment"):
        if f"/-/{k}" in inv:
            return k
    return None


def render_note(note, kind):
    c = note.get("content", {})
    lines, gap_bits = [], []
    keys = [k for k in REVIEW_FIELDS if k in c] + \
           [k for k in c if k not in REVIEW_FIELDS and k not in SKIP_FIELDS]
    for k in keys:
        v = val(c, k).strip()
        if not v:
            continue
        if len(v) < 60 and "\n" not in v:
            lines.append(f"- **{k}**: {v}")
        else:
            lines.append(f"- **{k}**:\n\n{indent(v)}\n")
        if kind == "Official_Review" and k in GAP_FIELDS:
            gap_bits.append((k, v))
    return lines, gap_bits


def indent(text):
    return "\n".join("  > " + line if line.strip() else "  >" for line in text.strip().splitlines())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-t", "--term", required=True, help="search term, e.g. watermark")
    ap.add_argument("-v", "--venue", action="append", required=True,
                    help="OpenReview venue id, e.g. ICLR.cc/2025/Conference (repeatable)")
    ap.add_argument("--max", type=int, default=20, help="max submissions per venue")
    ap.add_argument("--status", choices=["all", "accepted", "rejected", "withdrawn"], default="all",
                    help="rejected also keeps 'Submitted to ...' (rejected papers keep that label)")
    ap.add_argument("--require", action="append", default=[],
                    help="keep only submissions whose title/abstract/keywords contain this (repeatable); "
                         "the OpenReview search matches ANY word of --term")
    ap.add_argument("--no-comments", action="store_true", help="skip author rebuttals / discussion")
    ap.add_argument("--out", default="openreview_reviews")
    args = ap.parse_args()

    token = None
    try:
        token = login()
    except Exception as e:
        print(f"[warn] login failed: {e}", file=sys.stderr)

    md = [f"# OpenReview reviews — term `{args.term}`", "",
          "Venues: " + ", ".join(args.venue), ""]
    gap_md = [f"# Reviewer-raised weaknesses — term `{args.term}`", "",
              "One entry per review field. Cluster these: a weakness raised across many papers "
              "is a field-level gap, not a single paper's flaw.", ""]
    dump, blocked = [], False

    for venue in args.venue:
        try:
            subs = search(args.term, venue, min(500, args.max * (15 if args.require else 3)))
        except Exception as e:
            print(f"[warn] search failed for {venue}: {e}", file=sys.stderr)
            continue
        want = {"all": None, "accepted": {"accepted"}, "withdrawn": {"withdrawn"},
                "rejected": {"rejected", "rejected-or-pending"}}[args.status]
        subs = [s for s in subs if want is None or status_of(val(s["content"], "venue")) in want]
        if args.require:
            def text(s):
                return " ".join(val(s["content"], k) for k in ("title", "abstract", "keywords")).lower()
            subs = [s for s in subs if all(r.lower() in text(s) for r in args.require)]
        subs = subs[:args.max]
        md += [f"## {venue} — {len(subs)} submissions", ""]
        for s in subs:
            c = s["content"]
            title, venue_str = val(c, "title"), val(c, "venue")
            forum_url = f"https://openreview.net/forum?id={s['id']}"
            md += [f"### {title}", "", f"{venue_str} — {forum_url}", "",
                   f"**Keywords:** {val(c, 'keywords')}", "",
                   f"**Abstract.** {val(c, 'abstract')[:1500]}", ""]
            rec = {"venue": venue, "forum": s["id"], "title": title, "status": venue_str,
                   "abstract": val(c, "abstract"), "notes": []}
            if blocked:
                dump.append(rec)
                continue
            try:
                notes = call("GET", "/notes", {"forum": s["id"], "limit": 1000}, token=token).get("notes", [])
                time.sleep(0.5)
            except Challenge:
                blocked = True
                md += ["_Reviews not downloaded: OpenReview requires login / human verification. "
                       "See the note at the end._", ""]
                dump.append(rec)
                continue
            order = {"Decision": 0, "Meta_Review": 1, "Official_Review": 2, "Rebuttal": 3,
                     "Official_Comment": 4, "Public_Comment": 5}
            picked = [(kind_of(n), n) for n in notes if kind_of(n)]
            if args.no_comments:
                picked = [(k, n) for k, n in picked if k not in ("Rebuttal", "Official_Comment", "Public_Comment")]
            for kind, n in sorted(picked, key=lambda x: order[x[0]]):
                lines, gaps = render_note(n, kind)
                if not lines:
                    continue
                who = (n.get("signatures") or ["?"])[0].rsplit("/", 1)[-1]
                md += [f"#### {kind} ({who})", ""] + lines + [""]
                for field, text in gaps:
                    gap_md += [f"- [{title[:80]}] ({venue_str}) **{field}**:", indent(text), ""]
                rec["notes"].append({"kind": kind, "by": who,
                                     "content": {k: val(n["content"], k) for k in n.get("content", {})}})
            dump.append(rec)

    if blocked:
        md += ["---", "",
               "**Reviews were not downloaded.** OpenReview answered with a human-verification "
               "challenge. Either set `OPENREVIEW_USERNAME` / `OPENREVIEW_PASSWORD` (your own account) "
               "and re-run, or open the forum links above in a browser, complete the check yourself, "
               "and save or paste the reviews for analysis."]
    with open(args.out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    with open(args.out + "_weaknesses.md", "w", encoding="utf-8") as f:
        f.write("\n".join(gap_md))
    with open(args.out + ".json", "w", encoding="utf-8") as f:
        json.dump(dump, f, ensure_ascii=False, indent=1)
    n_rev = sum(1 for r in dump for x in r["notes"] if x["kind"] == "Official_Review")
    print(f"wrote {args.out}.md, {args.out}_weaknesses.md, {args.out}.json "
          f"({len(dump)} submissions, {n_rev} reviews{'; reviews blocked — see note' if blocked else ''})")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    main()
