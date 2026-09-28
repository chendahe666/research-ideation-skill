#!/usr/bin/env python3
"""Pull the self-admitted weaknesses out of arXiv papers.

For each paper, fetches the arXiv HTML rendering (arxiv.org/html, falling back to
ar5iv for older papers) and extracts the sections authors use to admit what their
method does not do: Limitations, Failure cases, Future work, Discussion,
Conclusion, Broader impact — including bold run-in paragraphs such as
"**Limitations.** Our method ...". Writes one markdown file for gap mining.

Standard library only. Examples:
  python extract_limitations.py 2409.04109 2506.20803
  python extract_limitations.py https://arxiv.org/abs/2608.17447 --out lim.md
  python extract_limitations.py --scan field_scan.json          # arXiv papers found by lit_scan.py
  python extract_limitations.py --ids-file ids.txt --max-chars 4000
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser

UA = "research-ideation-skill/1.0 (extract_limitations.py)"
SECTION_RE = re.compile(
    r"limitation|failure|future (work|direction)|discussion|conclusion|broader impact|"
    r"societal impact|open (problem|question|challenge)|threats? to validity|weakness",
    re.I)
RUNIN_RE = re.compile(
    r"^\s*(limitations?( and future work)?|failure (cases?|modes?)|future (work|directions?)|"
    r"broader impacts?|discussion|open (problems?|questions?))\s*[.:]", re.I)
ARXIV_ID_RE = re.compile(r"(\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})(v\d+)?", re.I)


class Blocks(HTMLParser):
    """Flattens LaTeXML HTML into ("h", level, text) and ("p", text) blocks."""

    SKIP = {"script", "style", "figure", "table", "nav", "footer", "header"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.buf = []
        self.heading = None      # level while inside <hN>
        self.skip_depth = 0
        self.math_depth = 0
        self.title = ""
        self.in_title = False

    def flush(self):
        text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        self.buf = []
        if not text:
            return
        if self.heading is not None:
            self.blocks.append(("h", self.heading, text))
        else:
            self.blocks.append(("p", text))

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True
        if self.skip_depth:
            if tag in self.SKIP:
                self.skip_depth += 1
            return
        if tag in self.SKIP:
            self.skip_depth = 1
            return
        if tag == "math":
            if self.math_depth == 0:
                alt = dict(attrs).get("alttext")
                if alt:
                    self.buf.append(f" ${alt}$ ")
            self.math_depth += 1
            return
        if re.fullmatch(r"h[1-6]", tag):
            self.flush()
            self.heading = int(tag[1])
        elif tag in ("p", "div", "li", "section", "br"):
            self.flush()

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if self.skip_depth:
            if tag in self.SKIP:
                self.skip_depth -= 1
            return
        if tag == "math":
            self.math_depth = max(0, self.math_depth - 1)
            return
        if re.fullmatch(r"h[1-6]", tag):
            self.flush()
            self.heading = None
        elif tag in ("p", "div", "li", "section"):
            self.flush()

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.skip_depth or self.math_depth:
            return
        self.buf.append(data)


def fetch(url, retries=3):
    delay = 3.0
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise


def get_html(aid):
    for url in (f"https://arxiv.org/html/{aid}", f"https://ar5iv.labs.arxiv.org/html/{aid}"):
        page = fetch(url)
        # arXiv serves a stub page when HTML conversion failed; it has no ltx_section.
        if page and "ltx_section" in page:
            return url, page
    return None, None


def extract(page, max_chars):
    parser = Blocks()
    parser.feed(page)
    parser.flush()
    blocks = parser.blocks
    title = re.sub(r"\s+", " ", html.unescape(parser.title)).strip()
    abstract = ""
    for i, b in enumerate(blocks):
        if b[0] == "h" and b[2].lower().startswith("abstract"):
            abstract = " ".join(x[1] for x in blocks[i + 1:i + 4] if x[0] == "p")
            break

    found, used = [], set()
    for i, b in enumerate(blocks):
        if b[0] != "h" or not SECTION_RE.search(b[2]) or b[2].lower().startswith("abstract"):
            continue
        level, parts = b[1], []
        for j in range(i + 1, len(blocks)):
            nb = blocks[j]
            if nb[0] == "h" and nb[1] <= level:
                break
            parts.append(nb[2] if nb[0] == "h" else nb[1])
            used.add(j)
        used.add(i)
        found.append((b[2], " ".join(parts)))
    for i, b in enumerate(blocks):
        if b[0] == "p" and i not in used and RUNIN_RE.match(b[1]):
            found.append(("(run-in paragraph)", b[1]))

    trimmed = []
    for head, text in found:
        if len(text) > max_chars:
            text = text[:max_chars].rsplit(" ", 1)[0] + " ... [truncated]"
        trimmed.append((head, text))
    return title, abstract, trimmed


def ids_from_scan(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    ids = []
    for qd in data.get("queries", {}).values():
        papers = [p for era in qd.get("eras", {}).values() for p in era] + qd.get("newest", [])
        for p in papers:
            blob = " ".join(str(p.get(k) or "") for k in ("doi", "url", "id"))
            m = re.search(r"arxiv[./](\d{4}\.\d{4,5})", blob, re.I)
            if m:
                ids.append(m.group(1))
    return ids


def normalize(token):
    m = ARXIV_ID_RE.search(token)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*", help="arXiv ids or arXiv URLs")
    ap.add_argument("--ids-file", help="text file, one id/URL per line")
    ap.add_argument("--scan", help="JSON written by lit_scan.py; uses the arXiv papers in it")
    ap.add_argument("--max-chars", type=int, default=3000, help="per extracted section")
    ap.add_argument("--out", default="limitations.md")
    args = ap.parse_args()

    raw = list(args.ids)
    if args.ids_file:
        with open(args.ids_file, encoding="utf-8") as f:
            raw += [line.strip() for line in f if line.strip()]
    if args.scan:
        raw += ids_from_scan(args.scan)
    ids = []
    for t in raw:
        aid = normalize(t)
        if aid and aid not in ids:
            ids.append(aid)
    if not ids:
        sys.exit("no arXiv ids given")

    out = ["# Self-reported limitations / future work", "",
           "Extracted from arXiv HTML. These are what authors *admit*; reviewers usually find more "
           "(see openreview_reviews.py).", ""]
    ok = 0
    for n, aid in enumerate(ids, 1):
        print(f"[{n}/{len(ids)}] {aid}", file=sys.stderr)
        try:
            url, page = get_html(aid)
        except Exception as e:
            out += [f"## {aid}", "", f"_fetch failed: {e}_", ""]
            continue
        if not page:
            out += [f"## {aid}", "", f"_No HTML version. Read the PDF: https://arxiv.org/pdf/{aid}_", ""]
            continue
        title, abstract, sections = extract(page, args.max_chars)
        out += [f"## {title or aid}", "", f"arXiv {aid} — {url}", ""]
        if abstract:
            out += [f"**Abstract.** {abstract[:1200]}", ""]
        if not sections:
            out += ["_No limitations / future-work / conclusion section detected._", ""]
        for head, text in sections:
            out += [f"### {head}", "", text, ""]
        ok += 1
        time.sleep(1.5)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"wrote {args.out} ({ok}/{len(ids)} papers parsed)")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    main()
