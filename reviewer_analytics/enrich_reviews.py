"""
enrich_reviews.py — CrossRef DOI lookup for reviews with known titles.

Reads reviews.yaml, and for every entry that has a manuscript_title but no doi,
queries the CrossRef REST API to find the published paper's DOI.

Only writes DOIs back when CrossRef's match confidence is high (title similarity
> 0.85). Everything else stays untouched — no guesses, no false positives.

Requires: requests, pyyaml, python-Levenshtein (or difflib fallback)
Rate-limited to be a polite CrossRef citizen (1 req/sec + mailto tag).

Usage:
    python enrich_reviews.py                    # dry-run: print what would change
    python enrich_reviews.py --write            # actually update reviews.yaml
    python enrich_reviews.py --write --verbose  # show every lookup, including misses
"""
import sys
import time
import argparse
import difflib
from urllib.parse import quote

try:
    import yaml
except ImportError:
    sys.exit("pip install pyyaml")
try:
    import requests
except ImportError:
    sys.exit("pip install requests")

# Change this to your email — CrossRef routes requests with a mailto to the
# faster 'polite pool' and can contact you if your script misbehaves.
CROSSREF_MAILTO = "kalyanidhusia.bhu@gmail.com"

CROSSREF_URL = "https://api.crossref.org/works"
HEADERS = {"User-Agent": f"kalyani-reviewer-portfolio/1.0 (mailto:{CROSSREF_MAILTO})"}
MATCH_THRESHOLD = 0.85   # minimum title similarity to accept a DOI


def normalize_title(s: str) -> str:
    """Lowercase and strip punctuation for fair title comparison."""
    if not s:
        return ""
    keep = []
    for c in s.lower():
        if c.isalnum() or c.isspace():
            keep.append(c)
    return " ".join("".join(keep).split())


def title_similarity(a: str, b: str) -> float:
    """0.0 – 1.0 similarity between two normalized titles."""
    na, nb = normalize_title(a), normalize_title(b)
    if not na or not nb:
        return 0.0
    return difflib.SequenceMatcher(None, na, nb).ratio()


def query_crossref(title: str, issn: str = None, year: int = None) -> list[dict]:
    """Return top 5 CrossRef candidates for a title, optionally filtered by ISSN/year."""
    params = {
        "query.bibliographic": title,
        "rows": 5,
        "mailto": CROSSREF_MAILTO,
    }
    filters = []
    if issn:
        filters.append(f"issn:{issn}")
    if year:
        filters.append(f"from-pub-date:{year - 1}")   # allow published up to 1 year later
        filters.append(f"until-pub-date:{year + 2}")  # reviews often precede publication
    if filters:
        params["filter"] = ",".join(filters)

    try:
        r = requests.get(CROSSREF_URL, params=params, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.json().get("message", {}).get("items", [])
    except requests.RequestException as e:
        print(f"    ! CrossRef error: {e}", file=sys.stderr)
        return []


def find_best_match(candidates: list[dict], search_title: str) -> tuple[dict, float] | None:
    """Pick the highest-similarity CrossRef candidate above threshold."""
    if not candidates:
        return None
    best = None
    for item in candidates:
        titles = item.get("title", [])
        if not titles:
            continue
        cand_title = titles[0]
        sim = title_similarity(search_title, cand_title)
        if best is None or sim > best[1]:
            best = (item, sim)
    if best and best[1] >= MATCH_THRESHOLD:
        return best
    return None


def process_reviews(reviews: list[dict], write: bool, verbose: bool) -> tuple[list[dict], dict]:
    """Enrich reviews with DOIs. Returns (updated_reviews, stats)."""
    stats = {"checked": 0, "matched": 0, "already_had_doi": 0, "no_title": 0, "no_match": 0}
    updated = []

    for entry in reviews:
        entry = dict(entry)  # copy
        if entry.get("type") != "journal_review":
            updated.append(entry)
            continue

        title = entry.get("manuscript_title")
        if not title:
            stats["no_title"] += 1
            updated.append(entry)
            continue

        if entry.get("doi"):
            stats["already_had_doi"] += 1
            updated.append(entry)
            continue

        stats["checked"] += 1
        issn = entry.get("issn")
        year = entry.get("year")
        if verbose:
            print(f"  → {title[:70]}...")

        candidates = query_crossref(title, issn=issn, year=year)
        time.sleep(1.0)  # be polite

        result = find_best_match(candidates, title)
        if result:
            item, sim = result
            doi = item.get("DOI")
            entry["doi"] = doi
            entry["doi_confidence"] = round(sim, 3)
            entry.setdefault("evidence", []).append({
                "type": "crossref_lookup",
                "url": f"https://doi.org/{doi}",
                "description": f"DOI matched via CrossRef (title similarity {sim:.2f})",
            })
            stats["matched"] += 1
            print(f"  ✓ {doi}  ({sim:.2f})  {title[:60]}")
        else:
            stats["no_match"] += 1
            if verbose:
                print(f"  ✗ no match: {title[:60]}")

        updated.append(entry)

    return updated, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--yaml", default="reviews.yaml", help="Path to reviews.yaml (default: %(default)s)")
    ap.add_argument("--write", action="store_true", help="Actually write DOIs back (default: dry-run)")
    ap.add_argument("--verbose", action="store_true", help="Show every lookup, including misses")
    args = ap.parse_args()

    with open(args.yaml) as f:
        data = yaml.safe_load(f)

    if not data or "reviews" not in data:
        sys.exit(f"{args.yaml} missing top-level 'reviews' list")

    print(f"Loaded {len(data['reviews'])} entries from {args.yaml}")
    print(f"Mode: {'WRITE' if args.write else 'DRY-RUN'}\n")

    updated, stats = process_reviews(data["reviews"], args.write, args.verbose)

    print(f"\n---")
    print(f"Journal reviews checked (had a title, no DOI):   {stats['checked']}")
    print(f"DOI matches found via CrossRef:                  {stats['matched']}")
    print(f"Entries that already had a DOI:                  {stats['already_had_doi']}")
    print(f"Entries with no manuscript title (skipped):      {stats['no_title']}")
    print(f"Titles that got no CrossRef match:               {stats['no_match']}")

    if args.write and stats["matched"] > 0:
        data["reviews"] = updated
        with open(args.yaml, "w") as f:
            yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False, width=100)
        print(f"\n✓ Wrote {stats['matched']} new DOIs to {args.yaml}")
    elif not args.write:
        print(f"\n(dry run — pass --write to save changes)")


if __name__ == "__main__":
    main()
