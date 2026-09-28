"""
merge_csv.py — merge a source-specific review-history CSV into reviews.yaml.

Standard CSV shape (columns must exist, header row required):
    source_id       string or empty — a unique ID from the source (e.g. MDPI review ID)
    journal         string — journal name, exactly as you want it in the record
    issn            string or empty
    year            integer
    date            YYYY-MM-DD, YYYY-MM, or YYYY
    title           the manuscript title (this is what CrossRef needs)
    doi             optional, if known
    publisher_org   e.g. MDPI, Elsevier, Frontiers
    verified_by     comma-separated: e.g. "orcid,wos" or "mdpi_dashboard"

Behavior:
  - For each CSV row, tries to find a matching existing entry in reviews.yaml
    by (issn OR journal) + year + month. If matched: enrich (add title/doi/etc).
  - If no match: append as a new entry.
  - Never overwrites existing non-empty fields — only fills blanks.

Usage:
    python merge_csv.py mdpi_export.csv                # dry-run
    python merge_csv.py mdpi_export.csv --write        # apply merge
    python merge_csv.py mdpi_export.csv --write --source mdpi_dashboard
"""
import sys
import csv
import argparse

try:
    import yaml
except ImportError:
    sys.exit("pip install pyyaml")


REQUIRED_COLS = {"journal", "year", "date", "title"}
OPTIONAL_COLS = {"source_id", "issn", "doi", "publisher_org", "verified_by"}


def load_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = set(reader.fieldnames or [])
        missing = REQUIRED_COLS - cols
        if missing:
            sys.exit(f"CSV missing required columns: {sorted(missing)}\nFound: {sorted(cols)}")
        return list(reader)


def find_match(csv_row: dict, entries: list[dict]) -> int | None:
    """Return the index of the first matching entry in `entries`, or None."""
    year = int(csv_row["year"]) if csv_row.get("year") else None
    if not year:
        return None
    month = None
    date = csv_row.get("date", "")
    if len(date) >= 7 and date[5] == "-":
        try:
            month = int(date[5:7])
        except ValueError:
            pass
    issn = (csv_row.get("issn") or "").strip()
    journal = (csv_row.get("journal") or "").strip().lower()

    for i, e in enumerate(entries):
        if e.get("type") != "journal_review":
            continue
        if e.get("doi") or e.get("manuscript_title"):
            continue  # already enriched, skip to keep matches unique
        if e.get("year") != year:
            continue
        # Match by ISSN first, then by journal name
        e_issn = (e.get("issn") or "").strip()
        e_journal = (e.get("journal") or "").strip().lower()
        if issn and e_issn and issn != e_issn:
            continue
        if not issn and journal and e_journal and journal not in e_journal and e_journal not in journal:
            continue
        # Month check if both have it
        e_date = e.get("date") or ""
        if month and len(e_date) >= 7 and e_date[5] == "-":
            try:
                e_month = int(e_date[5:7])
                if e_month != month:
                    continue
            except ValueError:
                pass
        return i
    return None


def enrich_entry(entry: dict, csv_row: dict, default_source: str) -> dict:
    """Fill in title, DOI, and other fields on an existing entry from CSV data."""
    entry = dict(entry)
    if csv_row.get("title") and not entry.get("manuscript_title"):
        entry["manuscript_title"] = csv_row["title"].strip()
    if csv_row.get("doi") and not entry.get("doi"):
        entry["doi"] = csv_row["doi"].strip()

    # Merge verified_by (keep existing, add new)
    new_verified = [v.strip() for v in (csv_row.get("verified_by") or default_source).split(",") if v.strip()]
    existing_verified = set(entry.get("verified_by", []))
    combined = list(existing_verified) + [v for v in new_verified if v not in existing_verified]
    entry["verified_by"] = combined

    entry.setdefault("evidence", []).append({
        "type": f"csv_import_{default_source}",
        "source_id": csv_row.get("source_id", ""),
        "description": f"Enriched from {default_source} CSV export",
    })
    return entry


def make_new_entry(csv_row: dict, default_source: str) -> dict:
    """Build a fresh journal_review entry when no existing entry matches."""
    year = int(csv_row["year"])
    title = csv_row.get("title", "").strip()
    journal = csv_row["journal"].strip()
    slug_title = "".join(c if c.isalnum() else "-" for c in title.lower())[:40].strip("-") or "untitled"

    entry = {
        "id": f"{year}-{default_source}-{slug_title}",
        "type": "journal_review",
        "year": year,
        "date": csv_row.get("date", str(year)),
        "role": "reviewer",
        "journal": journal,
        "manuscript_title": title,
    }
    if csv_row.get("publisher_org"):
        entry["publisher_org"] = csv_row["publisher_org"].strip()
    if csv_row.get("issn"):
        entry["issn"] = csv_row["issn"].strip()
    if csv_row.get("doi"):
        entry["doi"] = csv_row["doi"].strip()

    verified = [v.strip() for v in (csv_row.get("verified_by") or default_source).split(",") if v.strip()]
    entry["verified_by"] = verified
    entry["evidence"] = [{
        "type": f"csv_import_{default_source}",
        "source_id": csv_row.get("source_id", ""),
        "description": f"New entry from {default_source} CSV export",
    }]
    entry["cv_line"] = f"Peer reviewer, {journal}, {csv_row.get('date', str(year))}."
    return entry


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv_path", help="CSV file to merge")
    ap.add_argument("--yaml", default="reviews.yaml", help="Path to reviews.yaml (default: %(default)s)")
    ap.add_argument("--source", default="csv_import", help="Source tag for verified_by (default: %(default)s)")
    ap.add_argument("--write", action="store_true", help="Actually write changes (default: dry-run)")
    args = ap.parse_args()

    rows = load_csv(args.csv_path)
    print(f"Loaded {len(rows)} rows from {args.csv_path}")

    with open(args.yaml) as f:
        data = yaml.safe_load(f)
    entries = list(data["reviews"])
    print(f"Loaded {len(entries)} existing entries from {args.yaml}\n")

    matched = 0
    appended = 0
    for row in rows:
        idx = find_match(row, entries)
        if idx is not None:
            entries[idx] = enrich_entry(entries[idx], row, args.source)
            matched += 1
            print(f"  ↺ enriched: {row.get('title','')[:50]}")
        else:
            entries.append(make_new_entry(row, args.source))
            appended += 1
            print(f"  + added:    {row.get('title','')[:50]}")

    print(f"\n---")
    print(f"Enriched existing entries: {matched}")
    print(f"Appended new entries:      {appended}")
    print(f"Total entries after merge: {len(entries)}")

    if args.write:
        data["reviews"] = entries
        with open(args.yaml, "w") as f:
            yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False, width=100)
        print(f"\n✓ Wrote {args.yaml}")
    else:
        print(f"\n(dry run — pass --write to save changes)")


if __name__ == "__main__":
    main()
