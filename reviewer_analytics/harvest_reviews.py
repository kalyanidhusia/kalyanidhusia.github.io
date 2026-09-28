"""
harvest_reviews.py — merge Web of Science JSON export + MDPI reviewer table
into reviews.yaml, enriching existing ORCID entries with real titles.

Data sources it understands:

1. Web of Science CV JSON — from https://webofscience.com/wos/op/researcher-recognition/researcher-profile
   Export button → "Researcher CV (JSON)". Contains full titles for every
   review WoS Reviewer Recognition has verified.

2. MDPI reviewer table — copy your MDPI reviewer dashboard's review history
   into a tab-separated file with columns:
       Manuscript-ID  Journal  Title  Invited Date  Review Date  Manuscript Status  ORCID Status

Behavior:
  - For each incoming record, find the best-matching existing entry in
    reviews.yaml by (year + journal + month, or ISSN if present).
  - If matched: enrich in place (fill in title, MDPI manuscript ID,
    accepted/rejected status). Never overwrite non-empty fields.
  - If MDPI title is truncated ("... ") but WoS has the same review with
    the FULL title, use the WoS version.
  - Every save updates verified_by to add 'wos' and/or 'mdpi_dashboard'.
  - If no match: append as a new entry (rare — happens when MDPI has a
    review that never made it into ORCID for whatever reason).

Usage:
    python harvest_reviews.py --wos wos.json --mdpi mdpi.tsv                # dry-run
    python harvest_reviews.py --wos wos.json --mdpi mdpi.tsv --write        # apply
    python harvest_reviews.py --wos wos.json --write                        # WoS only
    python harvest_reviews.py --mdpi mdpi.tsv --write                       # MDPI only
"""
import sys
import re
import json
import csv
import argparse
import difflib
from typing import Optional, List, Dict, Tuple

try:
    import yaml
except ImportError:
    sys.exit("pip install pyyaml")


# Journal name normalization — MDPI's dashboard uses lowercase slugs
# ("genes", "ijms", "biomolecules") while ORCID and WoS use proper names.
MDPI_JOURNAL_NAMES = {
    "genes": "Genes",
    "ijms": "International Journal of Molecular Sciences",
    "biomolecules": "Biomolecules",
    "cancers": "Cancers",
    "curroncol": "Current Oncology",
    "ai": "AI",
    "biology": "Biology",
    "computers": "Computers",
    "electronics": "Electronics",
    "futureinternet": "Future Internet",
    "metabolites": "Metabolites",
    "ejihpe": "European Journal of Investigation in Health Psychology and Education",
    "information": "Information",
    "cimb": "Current Issues in Molecular Biology",
    "virtualworlds": "Virtual Worlds",
    "BDCC": "Big Data and Cognitive Computing",
    "ijerph": "International Journal of Environmental Research and Public Health",
}

# MDPI journal slug → ISSN. Populated on each MDPI record so that matching
# against ORCID uses the ISSN as the primary key (avoiding false positives
# from journal-name substring collisions like MDPI Computers vs Elsevier's
# Computers in Biology and Medicine).
MDPI_SLUG_ISSN = {
    "genes": "2073-4425",
    "ijms": "1422-0067",
    "biomolecules": "2218-273X",
    "cancers": "2072-6694",
    "curroncol": "1718-7729",
    "ai": "2673-2688",
    "biology": "2079-7737",
    "computers": "2073-431X",
    "electronics": "2079-9292",
    "futureinternet": "1999-5903",
    "metabolites": "2218-1989",
    "ejihpe": "2254-9625",
    "information": "2078-2489",
    "cimb": "1467-3045",
    "virtualworlds": "2813-2084",
    "BDCC": "2504-2289",
    "ijerph": "1660-4601",
}

# Journal name → canonical ISSN, used to match against ORCID entries where
# only the ISSN is known (journal field like "ISSN:2504-2289"). Add more here
# as you encounter them — the harvest script warns about unmapped WoS journals.
JOURNAL_ISSN_MAP = {
    # MDPI (usually eISSN)
    "big data and cognitive computing": "2504-2289",
    "biology": "2079-7737",
    "computers": "2073-431X",
    "electronics": "2079-9292",
    "future internet": "1999-5903",
    "metabolites": "2218-1989",
    "european journal of investigation in health psychology and education": "2254-9625",
    "information": "2078-2489",
    "ai": "2673-2688",
    "virtual worlds": "2813-2084",
    "current issues in molecular biology": "1467-3045",
    "current oncology": "1718-7729",
    "international journal of environmental research and public health": "1660-4601",
    # Elsevier
    "cytokine": "1043-4666",
    "biochemical and biophysical research communications": "0006-291X",
    "brain research": "0006-8993",
    "phytomedicine": "0944-7113",
    "biochimica et biophysica acta reviews on cancer": "0304-419X",
    "biochimica et biophysica acta: reviews on cancer": "0304-419X",
    "journal of controlled release": "0168-3659",
    "biochemistry and biophysics reports": "2405-5808",
    "human gene": "2773-0441",
    "computers in biology and medicine": "0010-4825",
    "computational biology and chemistry": "1476-9271",
    # RSC
    "rsc advances": "2046-2069",
    # Springer
    "medicinal chemistry research": "1054-2523",
}

MONTH_MAP = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
             "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}


def normalize_title(s: str) -> str:
    if not s:
        return ""
    out = []
    for c in s.lower():
        if c.isalnum() or c.isspace():
            out.append(c)
    return " ".join("".join(out).split())


def title_similarity(a: str, b: str) -> float:
    na, nb = normalize_title(a), normalize_title(b)
    if not na or not nb:
        return 0.0
    return difflib.SequenceMatcher(None, na, nb).ratio()


def strip_truncation(mdpi_title: str) -> str:
    """MDPI dashboard truncates long titles with ' ...' at the end."""
    return mdpi_title.replace(" ...", "").strip()


def parse_wos_date(d: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse 'Aug 2026' or 'Aug 2026' into (year, month)."""
    if not d:
        return None, None
    parts = d.strip().split()
    if len(parts) != 2:
        return None, None
    mon = MONTH_MAP.get(parts[0][:3].lower())
    try:
        year = int(parts[1])
    except ValueError:
        return None, None
    return year, mon


def parse_iso_date(d: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse '2026-04-24 06:00:13' into (year, month)."""
    if not d or len(d) < 7:
        return None, None
    try:
        return int(d[:4]), int(d[5:7])
    except ValueError:
        return None, None


# --------------------------------------------------------------------------- #
# Data source loaders
# --------------------------------------------------------------------------- #

def load_wos(path: str) -> List[Dict]:
    """Return list of normalized WoS review records."""
    with open(path) as f:
        data = json.load(f)
    raw = data.get("records", {}).get("review", {}).get("reviews", {}).get("review_list", [])
    out = []
    for r in raw:
        rounds = r.get("review_rounds", {}) or {}
        year, month = parse_wos_date(rounds.get("end_date") or rounds.get("start_date"))
        out.append({
            "source": "wos",
            "journal": r.get("journal", "").strip(),
            "title": r.get("title", "").strip(),
            "year": year,
            "month": month,
            "num_rounds": rounds.get("number_of_rounds"),
        })
    return out


def load_mdpi(path: str) -> List[Dict]:
    """Return list of normalized MDPI review records."""
    out = []
    with open(path, newline="", encoding="utf-8") as f:
        # Sniff delimiter (accepts tab or comma)
        sample = f.read(4096)
        f.seek(0)
        delim = "\t" if "\t" in sample.split("\n", 1)[0] else ","
        reader = csv.DictReader(f, delimiter=delim)
        for row in reader:
            title = strip_truncation(row.get("Title", ""))
            journal_slug = row.get("Journal", "").strip()
            journal = MDPI_JOURNAL_NAMES.get(journal_slug, journal_slug)
            issn = MDPI_SLUG_ISSN.get(journal_slug)
            year, month = parse_iso_date(row.get("Review Date", ""))
            manuscript_id = row.get("Manuscript-ID", "").strip()
            status = row.get("Manuscript Status", "").strip().lower()
            accepted = "online" in status or "published" in status
            rejected = "reject" in status
            out.append({
                "source": "mdpi",
                "journal": journal,
                "journal_slug": journal_slug,
                "issn": issn,
                "title": title,
                "title_truncated": title.endswith("...") or len(row.get("Title", "")) - len(title) > 3,
                "manuscript_id": manuscript_id,
                "year": year,
                "month": month,
                "status": "accepted" if accepted else ("rejected" if rejected else status),
            })
    return out


def parse_elsevier_date(d: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse '19 August 2026' into (year, month)."""
    if not d:
        return None, None
    m = re.match(
        r"(\d+)\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})",
        d.strip(),
    )
    if not m:
        return None, None
    year = int(m.group(3))
    month = MONTH_MAP.get(m.group(2)[:3].lower())
    return year, month


def load_elsevier(path: str) -> List[Dict]:
    """Return list of normalized Elsevier review records — one per review action (revision)."""
    out = []
    with open(path, newline="", encoding="utf-8") as f:
        sample = f.read(4096)
        f.seek(0)
        delim = "\t" if "\t" in sample.split("\n", 1)[0] else ","
        reader = csv.DictReader(f, delimiter=delim)
        for row in reader:
            journal = row.get("Journal", "").strip()
            title = row.get("Title", "").strip()
            revision = row.get("Revision", "").strip()
            date = row.get("Date", "").strip()
            year, month = parse_elsevier_date(date)
            try:
                rev_int = int(revision)
            except ValueError:
                rev_int = None
            out.append({
                "source": "elsevier",
                "journal": journal,
                "title": title,
                "review_round": rev_int,
                "year": year,
                "month": month,
                "date_str": date,
            })
    return out


def upgrade_mdpi_titles_from_wos(mdpi_recs: List[Dict], wos_recs: List[Dict]) -> Dict[str, str]:
    """
    For each MDPI record with a truncated title, try to find the corresponding
    WoS record and use the WoS full title instead. Returns {mdpi_manuscript_id: full_title}
    for the upgrades.
    """
    upgrades = {}
    for m in mdpi_recs:
        if not m["title"]:
            continue
        # Match by prefix (MDPI truncates around char 60-65)
        m_prefix = normalize_title(m["title"])[:min(len(m["title"]), 40)]
        best = None
        best_sim = 0.0
        for w in wos_recs:
            if w["journal"].lower() != m["journal"].lower():
                continue
            w_norm = normalize_title(w["title"])
            if w_norm.startswith(m_prefix):
                # Prefix match is a strong signal
                upgrades[m["manuscript_id"]] = w["title"]
                best = w
                break
            # Fall back to fuzzy similarity (catches title revisions)
            sim = title_similarity(m["title"], w["title"][:len(m["title"]) + 20])
            if sim > best_sim:
                best_sim = sim
                best = w
        # If prefix didn't hit, accept a fuzzy match only above 0.75
        if m["manuscript_id"] not in upgrades and best and best_sim >= 0.75:
            upgrades[m["manuscript_id"]] = best["title"]
    return upgrades


# --------------------------------------------------------------------------- #
# Matching against reviews.yaml
# --------------------------------------------------------------------------- #

def find_existing_entry(
    rec: Dict,
    entries: List[Dict],
    used_indices: set,
) -> Optional[int]:
    """
    Locate the reviews.yaml entry that best matches this incoming record.
    Match by (year + journal-or-ISSN + optional month), preferring exact-month.
    Skip entries already claimed by another incoming record this run.
    """
    year = rec.get("year")
    month = rec.get("month")
    journal = (rec.get("journal") or "").strip().lower()
    # ISSN on the record itself (MDPI records now carry it via slug map); else derive from journal
    rec_issn = (rec.get("issn") or "").strip() or JOURNAL_ISSN_MAP.get(journal)

    same_month_hit = None
    same_year_hit = None
    for i, e in enumerate(entries):
        if i in used_indices:
            continue
        if e.get("type") != "journal_review":
            continue
        if e.get("year") != year:
            continue
        e_journal = (e.get("journal") or "").strip().lower()
        e_issn = (e.get("issn") or "").strip()

        # Match logic (in priority order):
        #   1. Both records have the same ISSN — most reliable
        #   2. The ORCID entry is ISSN-only ("ISSN:xxxx") and the record's ISSN matches
        #   3. Journal names align — EXACT match, or safely-similar (both start same 25+ chars)
        # We do NOT accept loose substring matches (e.g. "Computers" ⊂ "Computers in Biology
        # and Medicine") because that led to real false-positive cross-journal merges.
        journal_match = False
        if rec_issn:
            if e_issn == rec_issn:
                journal_match = True
            elif e_journal == f"issn:{rec_issn.lower()}":
                journal_match = True
        if not journal_match and e_journal and journal and not e_journal.startswith("issn:"):
            if e_journal == journal:
                journal_match = True
            elif len(journal) >= 25 and len(e_journal) >= 25 and journal[:25] == e_journal[:25]:
                # Long journal names that share a substantial prefix — safe to match
                journal_match = True
        if not journal_match:
            continue

        e_date = str(e.get("date") or "")
        e_month = None
        if len(e_date) >= 7 and e_date[5] == "-":
            try:
                e_month = int(e_date[5:7])
            except ValueError:
                pass

        if month and e_month == month:
            same_month_hit = i
            break  # same-month is as good as it gets
        if same_year_hit is None:
            same_year_hit = i

    return same_month_hit if same_month_hit is not None else same_year_hit


def enrich_entry(entry: Dict, rec: Dict, wos_title_override: Optional[str] = None) -> Dict:
    """Fill in title, MDPI ID, verified_by, status. Never overwrite non-empty fields."""
    e = dict(entry)
    title = wos_title_override or rec.get("title")

    if title and not e.get("manuscript_title"):
        e["manuscript_title"] = title

    # Upgrade journal name if the current entry is ISSN-only
    current_journal = str(e.get("journal", ""))
    if current_journal.lower().startswith("issn:") and rec.get("journal"):
        e["journal"] = rec["journal"]

    if rec["source"] == "mdpi":
        if rec.get("manuscript_id") and not e.get("source_manuscript_id"):
            e["source_manuscript_id"] = rec["manuscript_id"]
        if rec.get("status") and not e.get("manuscript_status"):
            e["manuscript_status"] = rec["status"]

    if rec["source"] == "wos" and rec.get("num_rounds"):
        e.setdefault("review_rounds", rec["num_rounds"])

    if rec["source"] == "elsevier":
        if rec.get("review_round") is not None:
            # Elsevier tracks review actions per revision — store which round this entry represents
            e.setdefault("review_round", rec["review_round"])
        if rec.get("date_str") and not e.get("date"):
            e["date"] = rec["date_str"]

    # Merge verified_by
    tag_map = {"wos": "wos", "mdpi": "mdpi_dashboard", "elsevier": "elsevier_hub"}
    tag = tag_map.get(rec["source"])
    if tag:
        vb = list(e.get("verified_by", []))
        if tag not in vb:
            vb.append(tag)
        e["verified_by"] = vb

    # Add evidence trail
    ev = list(e.get("evidence", []))
    if rec["source"] == "wos":
        ev.append({
            "type": "wos_reviewer_cv",
            "description": "Title from Web of Science Researcher CV JSON export",
        })
    elif rec["source"] == "mdpi":
        ev.append({
            "type": "mdpi_dashboard",
            "manuscript_id": rec.get("manuscript_id", ""),
            "description": "Title and status from MDPI reviewer dashboard export",
        })
    elif rec["source"] == "elsevier":
        ev.append({
            "type": "elsevier_reviewer_hub",
            "review_round": rec.get("review_round"),
            "description": f"Title from Elsevier Reviewer Hub Review History Report (revision {rec.get('review_round')})",
        })
    e["evidence"] = ev
    return e


def make_new_entry(rec: Dict, wos_title_override: Optional[str] = None) -> Dict:
    """Build a fresh journal_review entry when no existing entry matches."""
    year = rec["year"]
    month = rec.get("month")
    title = wos_title_override or rec.get("title", "")
    journal = rec["journal"]
    date = f"{year}-{month:02d}" if month else str(year)

    slug_source = rec.get("manuscript_id") or normalize_title(title).replace(" ", "-")[:40] or "untitled"

    e = {
        "id": f"{year}-{rec['source']}-{slug_source}",
        "type": "journal_review",
        "year": year,
        "date": date,
        "role": "reviewer",
        "journal": journal,
        "manuscript_title": title,
    }
    if rec["source"] == "mdpi":
        e["source_manuscript_id"] = rec.get("manuscript_id", "")
        if rec.get("status"):
            e["manuscript_status"] = rec["status"]
        e["publisher_org"] = "MDPI"
        e["verified_by"] = ["mdpi_dashboard"]
    elif rec["source"] == "elsevier":
        if rec.get("review_round") is not None:
            e["review_round"] = rec["review_round"]
        e["publisher_org"] = "Elsevier"
        e["verified_by"] = ["elsevier_hub"]
    else:
        e["verified_by"] = ["wos"]
        if rec.get("num_rounds"):
            e["review_rounds"] = rec["num_rounds"]

    e["cv_line"] = f"Peer reviewer, {journal}, {date}."
    e["evidence"] = [{
        "type": f"{rec['source']}_import",
        "description": f"New entry from {rec['source']} import (no matching ORCID entry)",
    }]
    return e


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--wos", help="Path to Web of Science JSON CV export")
    ap.add_argument("--mdpi", help="Path to MDPI reviewer table (TSV or CSV)")
    ap.add_argument("--elsevier", help="Path to Elsevier Review History TSV (columns: Journal, Title, Revision, Date)")
    ap.add_argument("--yaml", default="reviews.yaml", help="reviews.yaml path (default: %(default)s)")
    ap.add_argument("--write", action="store_true", help="Actually write to reviews.yaml (default: dry-run)")
    ap.add_argument("--verbose", action="store_true", help="Show every match")
    args = ap.parse_args()

    if not any([args.wos, args.mdpi, args.elsevier]):
        sys.exit("Provide at least one of --wos, --mdpi, or --elsevier")

    wos_recs = load_wos(args.wos) if args.wos else []
    mdpi_recs = load_mdpi(args.mdpi) if args.mdpi else []
    elsevier_recs = load_elsevier(args.elsevier) if args.elsevier else []
    print(f"Loaded {len(wos_recs)} WoS records, {len(mdpi_recs)} MDPI records, {len(elsevier_recs)} Elsevier records")

    # Upgrade MDPI truncated titles from WoS where possible
    upgrades = upgrade_mdpi_titles_from_wos(mdpi_recs, wos_recs)
    if upgrades:
        print(f"Upgraded {len(upgrades)} MDPI truncated titles to WoS full titles")

    with open(args.yaml) as f:
        data = yaml.safe_load(f)
    entries = list(data["reviews"])
    print(f"Loaded {len(entries)} existing entries from {args.yaml}\n")

    stats = {"wos_enriched": 0, "wos_new": 0, "mdpi_enriched": 0, "mdpi_new": 0,
             "elsevier_enriched": 0, "elsevier_new": 0}
    wos_used = set()
    mdpi_used = set()
    elsevier_used = set()
    unmapped_journals = set()

    # Process WoS first (source of full titles); MDPI second (adds manuscript IDs + status);
    # Elsevier third (adds revision-round detail + titles for previously-unnamed entries).
    for rec in wos_recs:
        idx = find_existing_entry(rec, entries, wos_used)
        if idx is not None:
            entries[idx] = enrich_entry(entries[idx], rec)
            wos_used.add(idx)
            stats["wos_enriched"] += 1
            if args.verbose:
                print(f"  ✓ WoS→existing: {rec['journal'][:30]:30s} {rec['title'][:55]}")
        else:
            entries.append(make_new_entry(rec))
            stats["wos_new"] += 1
            journal_lower = (rec.get("journal") or "").lower()
            if journal_lower and journal_lower not in JOURNAL_ISSN_MAP:
                unmapped_journals.add(rec["journal"])
            if args.verbose:
                print(f"  + WoS→new:      {rec['journal'][:30]:30s} {rec['title'][:55]}")

    for rec in mdpi_recs:
        override = upgrades.get(rec["manuscript_id"])
        idx = find_existing_entry(rec, entries, mdpi_used)
        if idx is not None:
            entries[idx] = enrich_entry(entries[idx], rec, wos_title_override=override)
            mdpi_used.add(idx)
            stats["mdpi_enriched"] += 1
            if args.verbose:
                print(f"  ✓ MDPI→existing: [{rec['manuscript_id']}] {(override or rec['title'])[:55]}")
        else:
            entries.append(make_new_entry(rec, wos_title_override=override))
            stats["mdpi_new"] += 1
            if args.verbose:
                print(f"  + MDPI→new:     [{rec['manuscript_id']}] {(override or rec['title'])[:55]}")

    for rec in elsevier_recs:
        idx = find_existing_entry(rec, entries, elsevier_used)
        if idx is not None:
            entries[idx] = enrich_entry(entries[idx], rec)
            elsevier_used.add(idx)
            stats["elsevier_enriched"] += 1
            if args.verbose:
                print(f"  ✓ ELS→existing: {rec['journal'][:25]:25s} rev{rec['review_round']} {rec['title'][:50]}")
        else:
            entries.append(make_new_entry(rec))
            stats["elsevier_new"] += 1
            journal_lower = (rec.get("journal") or "").lower()
            if journal_lower and journal_lower not in JOURNAL_ISSN_MAP:
                unmapped_journals.add(rec["journal"])
            if args.verbose:
                print(f"  + ELS→new:      {rec['journal'][:25]:25s} rev{rec['review_round']} {rec['title'][:50]}")

    print(f"\n---")
    print(f"WoS records:      {stats['wos_enriched']} enriched existing / {stats['wos_new']} newly added")
    print(f"MDPI records:     {stats['mdpi_enriched']} enriched existing / {stats['mdpi_new']} newly added")
    print(f"Elsevier records: {stats['elsevier_enriched']} enriched existing / {stats['elsevier_new']} newly added")
    titled = sum(1 for e in entries if e.get("type") == "journal_review" and e.get("manuscript_title"))
    total = sum(1 for e in entries if e.get("type") == "journal_review")
    print(f"\nAfter merge: {titled}/{total} journal reviews now have titles ({100*titled/max(total,1):.0f}%)")
    print(f"Total entries: {len(entries)}")

    if unmapped_journals:
        print(f"\n⚠  Journals not in JOURNAL_ISSN_MAP (added as new entries — may be genuine, or may need mapping):")
        for j in sorted(unmapped_journals):
            print(f"   - {j!r}")
        print(f"   To match against ISSN-only ORCID entries, add these to JOURNAL_ISSN_MAP at the top of this script.")

    if args.write:
        data["reviews"] = entries
        with open(args.yaml, "w") as f:
            yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False, width=100, allow_unicode=True)
        print(f"\n✓ Wrote {args.yaml}")
    else:
        print(f"\n(dry run — pass --write to save changes)")


if __name__ == "__main__":
    main()
