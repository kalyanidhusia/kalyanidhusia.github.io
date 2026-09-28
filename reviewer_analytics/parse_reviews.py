"""Parse ORCID peer-review XML files into a single reviews.yaml master file."""
import os, glob, re
from xml.etree import ElementTree as ET
from collections import defaultdict, Counter

NS = {
    "pr": "http://www.orcid.org/ns/peer-review",
    "c":  "http://www.orcid.org/ns/common",
}

def first(root, path, default=""):
    el = root.find(path, NS)
    if el is None or el.text is None:
        return default
    return el.text.strip()

# ISSN -> journal name lookup, built as we go from source hints + a manual map for
# known bioinformatics/CB venues. We'll enrich this from context and leave gaps.
ISSN_TO_JOURNAL = {
    "1476-9271": "Computational Biology and Chemistry",
    "1367-4803": "Bioinformatics (OUP)",
    "1471-2105": "BMC Bioinformatics",
    "1471-2164": "BMC Genomics",
    "1471-2148": "BMC Evolutionary Biology",
    "1471-2199": "BMC Molecular Biology",
    "1553-7358": "PLOS Computational Biology",
    "1932-6203": "PLOS ONE",
    "1422-0067": "International Journal of Molecular Sciences (IJMS)",
    "2218-273X": "Biomolecules",
    "2072-6694": "Cancers",
    "2073-4425": "Genes",
    "2075-4418": "Diagnostics",
    "2073-4344": "Catalysts",
    "1660-4601": "International Journal of Environmental Research and Public Health",
    "1420-3049": "Molecules",
    "2076-2607": "Microorganisms",
    "2076-3417": "Applied Sciences",
    "2077-0383": "Journal of Clinical Medicine",
    "2079-9284": "Cosmetics",
    "2079-6382": "Antibiotics",
    "2076-393X": "Vaccines",
    "1424-8247": "Pharmaceuticals",
    "2223-7747": "Plants",
    "2313-7673": "Biomimetics",
    "0888-7543": "Genomics (Elsevier)",
    "1873-5347": "Genomics (Elsevier, online)",
    "1096-0961": "Microbial Pathogenesis",
    "0882-4010": "Microbial Pathogenesis (print)",
    "1873-2941": "Microbiological Research (online)",
    "0944-5013": "Microbiological Research",
    "1873-2917": "Journal of Molecular Graphics and Modelling (online)",
    "1093-3263": "Journal of Molecular Graphics and Modelling",
    "1476-4598": "Molecular Cancer",
    "1471-2407": "BMC Cancer",
    "1755-8794": "BMC Medical Genomics",
    "1755-3245": "BMC Research Notes",
    "1756-0500": "BMC Research Notes",
    "2045-2322": "Scientific Reports",
    "2050-7445": "Chemistry Central Journal",
    "1758-2946": "Journal of Cheminformatics",
    "1748-7188": "Algorithms for Molecular Biology",
    "1740-2530": "Systems and Synthetic Biology",
    "2296-889X": "Frontiers in Molecular Biosciences",
    "2296-4185": "Frontiers in Bioengineering and Biotechnology",
    "1664-8021": "Frontiers in Genetics",
    "2235-2988": "Frontiers in Cellular and Infection Microbiology",
    "1664-302X": "Frontiers in Microbiology",
    "1664-3224": "Frontiers in Immunology",
    "1664-042X": "Frontiers in Physiology",
    "1664-8714": "Frontiers in Medicine",
    "2296-2646": "Frontiers in Oncology",
    "2296-634X": "Frontiers in Cell and Developmental Biology",
    "1663-9812": "Frontiers in Pharmacology",
    "1662-453X": "Frontiers in Neuroscience",
    "1664-462X": "Frontiers in Plant Science",
    "1663-9812": "Frontiers in Pharmacology",
    "2571-581X": "Frontiers in Sustainable Food Systems",
}

def parse_review(path):
    """Return dict of extracted fields for a single peer-review XML."""
    tree = ET.parse(path)
    root = tree.getroot()

    put_code = root.attrib.get("put-code", "")
    visibility = root.attrib.get("visibility", "")

    source_name = first(root, "c:source/c:source-name")
    source_client = first(root, "c:source/c:source-client-id/c:path")

    role = first(root, "pr:reviewer-role")
    rtype = first(root, "pr:review-type")
    year = first(root, "pr:review-completion-date/c:year")
    month = first(root, "pr:review-completion-date/c:month")
    day = first(root, "pr:review-completion-date/c:day")

    group_id = first(root, "pr:review-group-id")   # usually issn:XXXX-XXXX
    org_name = first(root, "pr:convening-organization/c:name")
    org_city = first(root, "pr:convening-organization/c:address/c:city")
    org_country = first(root, "pr:convening-organization/c:address/c:country")

    issn = ""
    m = re.match(r"issn:([0-9X-]+)", group_id, flags=re.I)
    if m:
        issn = m.group(1)

    journal = ISSN_TO_JOURNAL.get(issn, "")

    date = year
    if month:
        date = f"{year}-{month.zfill(2)}"
        if day:
            date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    return {
        "put_code": put_code,
        "visibility": visibility,
        "source_name": source_name,
        "source_client": source_client,
        "role": role,
        "review_type": rtype,
        "year": year,
        "date": date,
        "issn": issn,
        "journal_from_lookup": journal,
        "convening_org": org_name,
        "org_location": ", ".join(x for x in (org_city, org_country) if x),
    }

files = sorted(glob.glob("peer_reviews/*.xml"))
records = [parse_review(f) for f in files]

# Stats
by_year = Counter(r["year"] for r in records if r["year"])
by_source = Counter(r["source_name"] for r in records if r["source_name"])
by_issn = Counter(r["issn"] for r in records if r["issn"])
by_org = Counter(r["convening_org"] for r in records if r["convening_org"])
unknown_issns = sorted({r["issn"] for r in records if r["issn"] and not r["journal_from_lookup"]})

print(f"Total peer_review records: {len(records)}")
print(f"\nBy year (top 12):")
for y, n in sorted(by_year.items()):
    print(f"  {y}: {n}")
print(f"\nBy source (deposit channel):")
for s, n in by_source.most_common():
    print(f"  {n:3d}  {s}")
print(f"\nBy convening organization (top 15):")
for s, n in by_org.most_common(15):
    print(f"  {n:3d}  {s}")
print(f"\nBy ISSN, top 20:")
for i, n in by_issn.most_common(20):
    jname = ISSN_TO_JOURNAL.get(i, "?")
    print(f"  {n:3d}  ISSN:{i:11s}  {jname}")
print(f"\nISSNs not in lookup table (need naming):")
for i in unknown_issns:
    n = by_issn.get(i, 0)
    print(f"  {n:3d}  ISSN:{i}")

# Save the raw records for the next step
import json
with open("reviews_raw.json", "w") as f:
    json.dump(records, f, indent=2, default=str)
print(f"\n\nWrote reviews_raw.json ({len(records)} records)")
