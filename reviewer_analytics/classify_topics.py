"""
classify_topics.py — assign a high-level `topic_area` to each titled review in reviews.yaml.

Six topic buckets (short, portfolio-friendly), assigned per-title using an explicit
rule table. Any review can be overridden by editing this script's TOPIC_OVERRIDES
dict below (by manuscript title prefix) — the classification is stored in the YAML
so overrides only need to be applied once.

Priority rules (highest wins when a title fits multiple):
  1. Cancer-focused subject → 'cancer_biology'
  2. Non-cancer disease subject → 'disease_biology'
  3. Immunology / signaling / receptor biology → 'immunology_signaling'
  4. Molecular structure / drug discovery / docking → 'structural_drug_discovery'
  5. AI/ML method is the primary contribution → 'ai_ml_methods'
  6. Bioinformatics tool / benchmark / methodology → 'bioinformatics_methods'
  7. Doesn't fit above → 'other'

Usage:
    python classify_topics.py                # dry-run
    python classify_topics.py --write        # actually write topic_area to reviews.yaml
    python classify_topics.py --show-untagged   # show titled entries that got 'other'
"""
import sys
import argparse
import re
try:
    import yaml
except ImportError:
    sys.exit("pip install pyyaml")


TOPIC_LABELS = {
    "cancer_biology": "Cancer biology & oncology",
    "disease_biology": "Disease biology (non-cancer)",
    "immunology_signaling": "Immunology & signaling",
    "structural_drug_discovery": "Structural bio & drug discovery",
    "ai_ml_methods": "AI/ML methods for biomedicine",
    "bioinformatics_methods": "Bioinformatics methods & tools",
    "other": "Other",
}

# Manual overrides (by title-prefix substring, case-insensitive). Take precedence
# over the keyword-matching rules below. Add entries here to correct
# misclassifications after reviewing the output.
TOPIC_OVERRIDES = {
    # DJ-1 & SH-SY5Y are Parkinson's-related (neurodegenerative)
    "DJ-1 deficiency in SH-SY5Y": "disease_biology",
    # PAQR4 review published in BBA Reviews on Cancer — venue makes it cancer-focused
    "PAQR4: from spatial regulation": "cancer_biology",
}

# Keyword rules, tried in priority order. First rule that matches wins.
# Each rule: (topic, [any-of these keywords must appear in normalized title])
RULES = [
    # ---- Priority 1: Cancer biology (any cancer subject) ----
    ("cancer_biology", [
        "cancer", "tumor", "tumour", "oncolog", "melanoma", "glioma",
        "carcinoma", "leukemia", "lymphoma", "metastasis", "metastatic",
        "pd-1", "pd-l1", "immunotherapy", "chemothera", "onco-",
        "tead4-yap", "egfr and her2", "hif-1a", "hif-1α",
    ]),
    # ---- Priority 2: Non-cancer disease biology (specific diseases) ----
    ("disease_biology", [
        "parkinson", "alzheimer", "diabet", "sarcopenia", "obesity",
        "asthma", "atheroscleros", "cardiovascular", "hypertension",
        "vascular dementia", "dermatitis", "atopic", "retinal", "rpe cells",
        "non-alcoholic fatty liver", "nafld", "arthritis", "osteoporosis",
        "psoriasis", "fibrosis", "gene therap", "diabetic foot",
        "cardiac", "neurodegener", "skeletal muscle aging", "aging",
        "microbiome",  # microbiome studies usually tied to a disease
    ]),
    # ---- Priority 3: Immunology / signaling / receptor biology ----
    ("immunology_signaling", [
        "tnf-tnfr", "tnf–tnfr", "tnf receptor", "tnfr signaling",
        "cytokine", "chemokine", "interleukin",
        "receptor ligand", "receptor-ligand", "ligand interaction",
        "immune cell", "antibody repertoire",
        "vaccine design", "chimeric vaccine",
        "tcr profiling",
    ]),
    # ---- Priority 4: Structural bio / drug discovery / docking ----
    ("structural_drug_discovery", [
        "molecular dynamics", "md simulations", "docking",
        "virtual screening", "high throughput virtual",
        "inhibitor", "inhibition", "peptide", "essential oil",
        "natural product", "natural compound",
        "drug design", "drug discovery", "drug candidates",
        "pharmacophore", "ligand-based",
        "structural basis", "structural and functional",
        "protein language model",  # embeddings for protein biology
        "alphafold", "intrinsically disordered protein",
        "idps", "conformational ensemble",
        "efflux pump", "biofilm",
        "network pharmacology",
        "antimalarial", "anti-mrsa",
        "cell-wall", "mycobacterium",
        "flumethasone", "targeting and normalization",  # drug delivery
        "tumor necrosis factor-alpha",  # EGCG paper, targeting TNF
        "co-receptor proteoglycan",
        "phytochemical", "phytocompound",
        "ginsenoside", "flavonoid", "polyphenol",
        "phytomedicine", "biotherap",
    ]),
    # ---- Priority 5: AI/ML methods (ML as the primary contribution) ----
    ("ai_ml_methods", [
        "machine learning", "deep learning", "transformer",
        "neural network", "autoencoder", "active learning",
        "xgboost", "svm", "support vector machine",
        "convolutional", "attention mechanism", "language model",
        "generative ai", "large language model", "llm",
        "reproducibility of machine",
        "gcnfold", "graph convolutional",
        "prediction of serine phosphorylation",
        "ai-methods over md",
        "sequence-only prediction",
        "framework for irregularly sampled",
        "heterogeneous network-based method",
        "prediction of coronavirus",
    ]),
    # ---- Priority 6: Bioinformatics methods / software / benchmarks ----
    ("bioinformatics_methods", [
        "framework for comparison", "tool", "benchmark",
        "cell-type deconvolution", "single cell", "single-cell",
        "scselector", "synthetic rna-seq",
        "differential co-expression",
        "predicting the pathway involvement", "metabolite",
        "integrated analysis of lncrnas",
        "systems biology employed", "sensory systems",
        "transcriptional regulation",
        "multi-omics integration",
    ]),
]

# Explicit overrides for known "other" cases (VR, metaverse, NLP unrelated to biomed,
# nanoplastics, science communication):
OTHER_KEYWORDS = [
    "metaverse", "virtual reality", "co-creation",
    "cloud computing in healthcare",
    "chinese entity recognition",
    "fake news",
    "nanoplastic", "micro/nanoplastic",
    "readability optimization", "layperson summaries",
    "historical sketch",
    "post-",  # e.g. "Comparative Analysis of AI Virtual Assistant and LLMs in Post-" (education)
    "scanning electron microscope examination",  # method comparison, not core
]


def normalize(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").lower()).strip()


def classify(title: str) -> str:
    t = normalize(title)
    # Manual overrides first
    for prefix, topic in TOPIC_OVERRIDES.items():
        if t.startswith(prefix.lower()):
            return topic
    # OTHER carve-outs first (before other rules would catch them)
    for kw in OTHER_KEYWORDS:
        if kw in t:
            return "other"
    # Priority-ordered rules
    for topic, keywords in RULES:
        for kw in keywords:
            if kw in t:
                return topic
    return "other"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--yaml", default="reviews.yaml")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--show-untagged", action="store_true",
                    help="Show titled entries classified as 'other' (candidates for correction)")
    args = ap.parse_args()

    with open(args.yaml) as f:
        data = yaml.safe_load(f)

    counts = {t: 0 for t in TOPIC_LABELS}
    other_titles = []
    titled = 0
    for e in data["reviews"]:
        if e.get("type") != "journal_review":
            continue
        title = e.get("manuscript_title")
        if not title:
            continue
        titled += 1
        topic = classify(title)
        e["topic_area"] = topic
        counts[topic] += 1
        if topic == "other":
            other_titles.append(title)

    print(f"Classified {titled} titled reviews:\n")
    for topic in ["cancer_biology", "ai_ml_methods", "structural_drug_discovery",
                  "disease_biology", "immunology_signaling", "bioinformatics_methods", "other"]:
        c = counts[topic]
        print(f"  {c:3d}  {TOPIC_LABELS[topic]}")

    if args.show_untagged and other_titles:
        print(f"\n'Other' entries ({len(other_titles)}):")
        for t in other_titles:
            print(f"  - {t[:100]}")

    if args.write:
        with open(args.yaml, "w") as f:
            yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False, width=100, allow_unicode=True)
        print(f"\n✓ Wrote topic_area to {args.yaml}")
    else:
        print(f"\n(dry run — pass --write to save)")


if __name__ == "__main__":
    main()
