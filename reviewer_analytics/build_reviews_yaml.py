"""Build the master reviews.yaml from ORCID XML + ARINBRE + Frontiers editorial."""
import glob, re, json
from xml.etree import ElementTree as ET
from collections import Counter, defaultdict

NS = {
    "pr": "http://www.orcid.org/ns/peer-review",
    "c":  "http://www.orcid.org/ns/common",
}

# Enriched ISSN lookup - what we could confirm
ISSN_TO_JOURNAL = {
    "1476-9271": "Computational Biology and Chemistry",
    "1538-0254": "Journal of Biomolecular Structure and Dynamics",
    "0010-4825": "Computers in Biology and Medicine",
    "2218-273X": "Biomolecules",
    "2073-4425": "Genes",
    "1422-0067": "International Journal of Molecular Sciences (IJMS)",
    "2072-6694": "Cancers",
    "2075-4418": "Diagnostics",
    "1420-3049": "Molecules",
    "2077-0383": "Journal of Clinical Medicine",
    "1660-4601": "Int. J. of Environmental Research and Public Health",
    "1471-2105": "BMC Bioinformatics",
    "2045-2322": "Scientific Reports",
    "2296-889X": "Frontiers in Molecular Biosciences",
    # ISSNs left as TBD (not yet named): 2405-5808, 2773-0441, 2504-2289,
    # 2813-2084, 2079-7737, 1043-4666, 1999-5903, 0006-291X, 0006-8993, and others.
    # These will appear as "ISSN:xxxx-xxxx" until you resolve them.
}

def first(root, path, default=""):
    el = root.find(path, NS)
    if el is None or el.text is None:
        return default
    return el.text.strip()

# Map deposit source to a normalized name
SOURCE_NORMALIZE = {
    "Elsevier Editorial": "elsevier",
    "Web of Science Researcher Profile Sync": "wos",
    "Web of Science Researcher Profiles": "wos",
    "Multidisciplinary Digital Publishing Institute": "mdpi",
    "Springer Nature @ Editorial Manager": "springer_nature",
}

def make_slug(year, source_norm, journal_hint, idx):
    """Deterministic id: <year>-<source>-<journalslug>-<seq>"""
    js = re.sub(r'[^a-z0-9]+', '-', journal_hint.lower()).strip('-')[:40] or "unnamed"
    return f"{year or 'undated'}-{source_norm}-{js}-{idx:03d}"

# Parse all ORCID XMLs
entries = []
files = sorted(glob.glob("0000-0002-8803-1295/peer_reviews/*.xml"))
if not files:
    # Fall back to the flat layout in case the folder was moved up one level
    files = sorted(glob.glob("peer_reviews/*.xml"))
counter_by_journal = Counter()

for i, path in enumerate(files, start=1):
    tree = ET.parse(path)
    root = tree.getroot()
    put_code = root.attrib.get("put-code", "")
    source_name = first(root, "c:source/c:source-name")
    source_norm = SOURCE_NORMALIZE.get(source_name, source_name.lower().replace(" ", "_"))
    role = first(root, "pr:reviewer-role") or "reviewer"
    year = first(root, "pr:review-completion-date/c:year")
    month = first(root, "pr:review-completion-date/c:month")
    group_id = first(root, "pr:review-group-id")
    org = first(root, "pr:convening-organization/c:name")
    issn = ""
    m = re.match(r"issn:([0-9X-]+)", group_id, flags=re.I)
    if m:
        issn = m.group(1)
    journal = ISSN_TO_JOURNAL.get(issn, "")
    journal_display = journal or (f"ISSN:{issn}" if issn else org or "Unknown")

    counter_by_journal[journal_display] += 1
    entry_seq = counter_by_journal[journal_display]

    date = year
    if month:
        date = f"{year}-{month.zfill(2)}"

    entry = {
        "id": make_slug(year, source_norm, journal or (f"issn-{issn}" if issn else "unknown"), i),
        "type": "journal_review",
        "year": int(year) if year else None,
        "date": date,
        "role": role,
        "journal": journal_display,
        "publisher_org": org,
        "issn": issn,
        "verified_by": ["orcid"],
        "evidence": [
            {"type": "orcid_put_code", "value": put_code},
            {"type": "orcid_source", "value": source_name},
        ],
        "cv_line": f"Peer reviewer, {journal_display}, {year}.",
    }
    # Add wos verification if source is wos
    if "wos" in source_norm or "web of science" in source_name.lower():
        if "wos" not in entry["verified_by"]:
            entry["verified_by"].append("wos")
    entries.append(entry)

# Sort entries by year desc, then journal
entries.sort(key=lambda e: (-(e["year"] or 0), e["journal"]))

# Add the ARINBRE entry
arinbre = {
    "id": "2026-arinbre-pilot",
    "type": "grant_review",
    "year": 2026,
    "date": "2026-01",
    "role": "reviewer",
    "program": "Arkansas INBRE Pilot Awards",
    "program_full_name": "Institutional Development Award (IDeA) Networks of Biomedical Research Excellence — Arkansas",
    "program_funding_source": "NIH NIGMS (P20)",
    "host_institution": "University of Arkansas for Medical Sciences (UAMS)",
    "cycle": "2026",
    "panel_size": 12,
    "proposals_reviewed": 9,
    "proposals_submitted": 18,
    "awards_funded_this_cycle": 6,
    "scoring_system": "NIH 1-9 scale",
    "review_platform": "RedCap",
    "award_mechanism": {
        "duration_months": 12,
        "max_direct_costs_usd": 50000,
        "start_date": "2026-05-01",
    },
    "panel_convener": {
        "name": "Jerry Ware, PhD",
        "title": "Associate Director, Arkansas INBRE",
        "affiliation": "UAMS, Physiology & Cell Biology",
    },
    "assignment_email_date": "2025-12-19",
    "reviews_completed_by": "2026-01-09",
    "sample_proposal_reviewed": "AI-Powered Histopathological Analysis of Brain Tumors",
    "verified_by": ["letter"],
    "evidence": [
        {"type": "email", "description": "Reviewer assignment email from Dr. Jerry Ware",
         "file": "Jerry_ARINBRE_REVIEWER.pdf", "date": "2025-12-19"},
    ],
    "cv_line": (
        "Reviewer, Arkansas INBRE Pilot Project Program, 2026 cycle. Reviewed 9 "
        "proposals on a 12-member panel; NIH-style 1-9 scoring, RedCap platform. "
        "Convened by Dr. Jerry Ware (Associate Director, AR INBRE)."
    ),
    "biosketch_line": (
        "Peer Reviewer, NIH IDeA-funded Arkansas INBRE Pilot Project Program "
        "(2026 cycle, UAMS). Reviewed 9 proposals under NIH-style criteria."
    ),
    "notes": (
        "No grant number to cite; evidence is the panel convener's assignment email "
        "retained on file. AR INBRE is an NIH NIGMS-funded IDeA program (P20)."
    ),
}

# Add the Frontiers editorial entry
frontiers_editorial = {
    "id": "2023-frontiers-molecular-biosciences-editorial",
    "type": "editorial",
    "start_date": "2023-09-18",
    "end_date": "2025",
    "role": "Review Editor",
    "editorial_board": "Biological Modeling and Simulation",
    "journal": "Frontiers in Molecular Biosciences",
    "journal_url": "https://www.frontiersin.org/journals/molecular-biosciences",
    "issn": "2296-889X",
    "manuscripts_handled": 7,
    "verified_by": ["wos", "frontiers"],
    "evidence": [
        {"type": "wos_record", "description": "Web of Science editorial-service record",
         "url": "https://www.webofscience.com/wos/op/peer-reviews/summary"},
        {"type": "frontiers_reviewer_id", "value": "640379",
         "description": "Frontiers reviewer ID; per-manuscript review pages linked in individual entries"},
    ],
    "cv_line": (
        "Review Editor, Editorial Board of Biological Modeling and Simulation, "
        "Frontiers in Molecular Biosciences (Sept 2023 – 2025). "
        "Handled 7 manuscript reviews on the section."
    ),
    "notes": "WoS-verified editorial service. Frontiers review portal shows 7 handled manuscripts during tenure; see individual frontiers_review entries.",
}

# UAMS Poster Session Judge (research day service)
uams_judge = {
    "id": "2025-uams-pa-student-research-day",
    "type": "judge",
    "year": 2025,
    "date": "2025-04-09",
    "role": "Judge",
    "event": "Poster Session, PA Student Research Day",
    "host_institution": "College of Health Professions, University of Arkansas for Medical Sciences (UAMS)",
    "verified_by": ["self"],
    "evidence": [
        {"type": "event", "description": "Judged poster session at UAMS PA Student Research Day",
         "date": "2025-04-09"},
    ],
    "cv_line": (
        "Judge, Poster Session, PA Student Research Day, College of Health Professions, "
        "University of Arkansas for Medical Sciences, April 9, 2025."
    ),
}

# MDPI Guest Editor role
mdpi_guest_editor = {
    "id": "2026-mdpi-ai-ml-bioinformatics-special-issue",
    "type": "guest_editor",
    "year": 2026,
    "role": "Guest Editor",
    "journal": "Journal of AI (MDPI)",
    "issue_title": "Machine Learning in Bioinformatics: Current Research and Development",
    "publisher_org": "MDPI",
    "journal_url": "https://www.mdpi.com/journal/ai/special_issues/6NS0U8I5Z4",
    "verified_by": ["self"],
    "evidence": [
        {"type": "url", "description": "MDPI Special Issue page",
         "url": "https://www.mdpi.com/journal/ai/special_issues/6NS0U8I5Z4"},
    ],
    "cv_line": (
        "Guest Editor, Special Issue \"Machine Learning in Bioinformatics: Current "
        "Research and Development\", Journal of AI, MDPI."
    ),
}

# Frontiers manuscript reviews - not in ORCID, handled during editorial tenure
# (7 during 2023-2025 Frontiers in Molecular Biosciences editorial board;
#  1 from 2022 predates the board tenure - journal TBD, likely Frontiers in Microbiology)
FRONTIERS_JOURNAL_MB = "Frontiers in Molecular Biosciences (Biological Modeling and Simulation section)"
FRONTIERS_JOURNAL_MB_URL = "https://www.frontiersin.org/journals/molecular-biosciences"
FRONTIERS_JOURNAL_MB_ISSN = "2296-889X"

frontiers_reviews_data = [
    # 2025
    ("1531793", "2025-04-23",
     "Successful prediction of LC8 binding to intrinsically disordered proteins illuminates AlphaFold's black box"),
    ("1542267", "2025-04-08",
     "Use of AI-Methods over MD Simulations in the Sampling of Conformational Ensembles in IDPs"),
    ("1549177", "2025-03-25",
     "Computational Analysis of the Structural-Functional Dynamics of a Co-receptor proteoglycan"),
    ("1543939", "2025-02-14",
     "Metabolite profiling, antimalarial potentials of Schleichera oleosa using LC-MS and GC-MS: in vitro, molecular docking and molecular dynamics"),
    # 2024
    ("1366588", "2024-04-04",
     "Characterisation of four peptides from milk fermented with kombucha cultures, and their metal complexes - In search of new biotherapeutics"),
    ("1278701", "2024-03-27",
     "Adenanthera pavonina-derived compounds to identify potential activators of mutated insulin receptor tyrosine kinase from diabetes mellitus: insight into the phytochemical analysis and in silico assays"),
    # 2023
    ("1258834", "2023-11-20",
     "Chimeric vaccine design against conserved TonB dependent receptor-like β-barrel domain from the outer membrane tbpA and hpuB proteins of Kingella kingae ATCC 23330"),
]

frontiers_review_entries = []
for review_id, date, title in frontiers_reviews_data:
    year = int(date[:4])
    frontiers_review_entries.append({
        "id": f"{year}-frontiers-mb-{review_id}",
        "type": "journal_review",
        "year": year,
        "date": date,
        "role": "reviewer",
        "journal": FRONTIERS_JOURNAL_MB,
        "publisher_org": "Frontiers",
        "issn": FRONTIERS_JOURNAL_MB_ISSN,
        "manuscript_title": title,
        "review_round": 2,
        "verified_by": ["frontiers"],
        "evidence": [
            {"type": "frontiers_review_url",
             "url": f"https://review.frontiersin.org/review/{review_id}/2/640379",
             "description": "Frontiers review portal page (reviewer-authenticated)"},
        ],
        "cv_line": f"Peer reviewer, {FRONTIERS_JOURNAL_MB}, {date}.",
        "notes": "Handled as Review Editor on the Biological Modeling and Simulation section board.",
    })

# Feb 2022 review predates Frontiers editorial board tenure (Sept 2023) -
# the journal is TBD (URL doesn't reveal it). Topic is bacterial genomics/regulation,
# most likely Frontiers in Microbiology - but flagged for user confirmation.
frontiers_review_entries.append({
    "id": "2022-frontiers-tbd-823240",
    "type": "journal_review",
    "year": 2022,
    "date": "2022-02-14",
    "role": "reviewer",
    "journal": "Frontiers (journal TBD)",
    "publisher_org": "Frontiers",
    "manuscript_title": "Sensory systems and transcriptional regulation in Escherichia coli",
    "review_round": 2,
    "verified_by": ["frontiers"],
    "evidence": [
        {"type": "frontiers_review_url",
         "url": "https://review.frontiersin.org/review/823240/2/640379",
         "description": "Frontiers review portal page (reviewer-authenticated)"},
    ],
    "cv_line": "Peer reviewer, Frontiers (journal TBD), 2022-02-14.",
    "notes": "Predates the Biological Modeling and Simulation editorial board tenure (Sept 2023). Topic (E. coli sensory systems) suggests Frontiers in Microbiology or similar - confirm exact journal from Frontiers reviewer dashboard.",
})

# Combine — special-service entries first, then journal reviews (including Frontiers)
master = [frontiers_editorial, mdpi_guest_editor, arinbre, uams_judge] + frontiers_review_entries + entries

# Write YAML manually (avoid pyyaml dependency, keep it deterministic)
def yaml_val(v, indent=0):
    pad = "  " * indent
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        if "\n" in v or v.startswith(" ") or len(v) > 100:
            body = "\n".join(pad + "  " + line for line in v.splitlines())
            return "|-\n" + body
        # Simple string - quote if it has special chars
        if any(c in v for c in ":#{}[],&*!|>'\"%@`"):
            return f'"{v.replace(chr(92), chr(92)+chr(92)).replace(chr(34), chr(92)+chr(34))}"'
        return v
    if isinstance(v, list):
        if not v:
            return "[]"
        out = []
        for item in v:
            if isinstance(item, (dict, list)):
                nested = yaml_dict(item, indent + 1) if isinstance(item, dict) else yaml_val(item, indent + 1)
                out.append(pad + "  - " + nested.lstrip())
            else:
                out.append(pad + "  - " + yaml_val(item, indent + 1))
        return "\n" + "\n".join(out)
    if isinstance(v, dict):
        return "\n" + yaml_dict(v, indent + 1)
    return str(v)

def yaml_dict(d, indent=0):
    pad = "  " * indent
    lines = []
    for k, v in d.items():
        if isinstance(v, dict):
            lines.append(f"{pad}{k}:")
            lines.append(yaml_dict(v, indent + 1))
        elif isinstance(v, list):
            if not v:
                lines.append(f"{pad}{k}: []")
            else:
                lines.append(f"{pad}{k}:")
                for item in v:
                    if isinstance(item, dict):
                        # First key on the dash line
                        keys = list(item.keys())
                        first_k = keys[0]
                        first_v = item[first_k]
                        if isinstance(first_v, (dict, list)):
                            lines.append(f"{pad}  - {first_k}:")
                            if isinstance(first_v, dict):
                                lines.append(yaml_dict(first_v, indent + 2))
                            else:
                                lines.append(pad + "    " + yaml_val(first_v, indent + 2).lstrip())
                        else:
                            lines.append(f"{pad}  - {first_k}: {yaml_val(first_v, indent + 2)}")
                        for k2 in keys[1:]:
                            v2 = item[k2]
                            if isinstance(v2, dict):
                                lines.append(f"{pad}    {k2}:")
                                lines.append(yaml_dict(v2, indent + 3))
                            elif isinstance(v2, list):
                                lines.append(f"{pad}    {k2}:{yaml_val(v2, indent + 2)}")
                            else:
                                rendered = yaml_val(v2, indent + 2)
                                if "\n" in rendered:
                                    lines.append(f"{pad}    {k2}: {rendered}")
                                else:
                                    lines.append(f"{pad}    {k2}: {rendered}")
                    else:
                        lines.append(f"{pad}  - {yaml_val(item, indent + 1)}")
        else:
            rendered = yaml_val(v, indent)
            if rendered.startswith("|-"):
                lines.append(f"{pad}{k}: {rendered}")
            else:
                lines.append(f"{pad}{k}: {rendered}")
    return "\n".join(lines)

with open("reviews.yaml", "w") as f:
    f.write("# Master peer review record for Kalyani Dhusia (ORCID 0000-0002-8803-1295)\n")
    f.write(f"# Auto-generated. {len(master)} entries: 1 editorial + 1 grant review + {len(entries)} journal reviews.\n")
    f.write(f"# ORCID export date: 2026-09-28. Fill unnamed ISSN journals by hand as you resolve them.\n\n")
    f.write("reviews:\n")
    for entry in master:
        f.write("\n")
        # Emit as list item
        keys = list(entry.keys())
        first_k = keys[0]
        first_v = entry[first_k]
        f.write(f"  - {first_k}: {yaml_val(first_v, 2)}\n")
        for k in keys[1:]:
            v = entry[k]
            if isinstance(v, dict):
                f.write(f"    {k}:\n")
                f.write(yaml_dict(v, 3) + "\n")
            elif isinstance(v, list):
                if not v:
                    f.write(f"    {k}: []\n")
                else:
                    f.write(f"    {k}:\n")
                    for item in v:
                        if isinstance(item, dict):
                            item_keys = list(item.keys())
                            fk = item_keys[0]
                            fv = item[fk]
                            f.write(f"      - {fk}: {yaml_val(fv, 4)}\n")
                            for k2 in item_keys[1:]:
                                v2 = item[k2]
                                f.write(f"        {k2}: {yaml_val(v2, 4)}\n")
                        else:
                            f.write(f"      - {yaml_val(item, 3)}\n")
            else:
                rendered = yaml_val(v, 2)
                if rendered.startswith("|-"):
                    f.write(f"    {k}: {rendered}\n")
                else:
                    f.write(f"    {k}: {rendered}\n")

# Also emit summary stats
total = len(entries)
by_year = Counter(e["year"] for e in entries)
by_journal = Counter(e["journal"] for e in entries)
by_verified = Counter(tuple(sorted(e["verified_by"])) for e in entries)

print(f"Wrote reviews.yaml with {len(master)} total entries:")
print(f"  1 editorial (Frontiers)")
print(f"  1 grant review (ARINBRE)")
print(f"  {total} journal reviews from ORCID")
print(f"\nJournal reviews by year:")
for y, n in sorted(by_year.items(), reverse=True):
    print(f"  {y}: {n}")
print(f"\nTop 12 journals:")
for j, n in by_journal.most_common(12):
    print(f"  {n:3d}  {j}")
print(f"\nVerification coverage of journal reviews:")
for v, n in by_verified.most_common():
    print(f"  {n:3d}  {list(v)}")

