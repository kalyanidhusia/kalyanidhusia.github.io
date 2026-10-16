# Pedagogy: how each game teaches

Every module follows the same loop, by design:

1. **Learn** — a flashcard states the concept, the learning objectives, and how to play, *before* any gameplay.
2. **Play** — the core mechanic *is* the biological rule being taught. Failure messages teach ("that base doesn't pair"), and each game grants practice grace before mistakes count.
3. **Check** — a six-question quiz (one question at a time, pass at 5/6, per-question explanations, retakes allowed).
4. **Honesty** — every module names its simplifications explicitly, on the win screen and in the footer.

This loop is what makes the gamification pedagogically defensible rather than decorative: the player cannot win without exercising the concept, and the module never claims more biological fidelity than it has.

All modules are single-file HTML (no build step, no dependencies, no tracking, zero PII), mobile-first (HTML-DOM text, devicePixelRatio-aware canvas, touch + keyboard controls), and work offline once loaded.

---

## Module 1 — Polymerase Runner (Transcription)

**Concept.** RNA polymerase reads a DNA template and synthesizes mRNA: bases pair by hydrogen bonds (A–T with 2, C–G with 3), and thymine (T) is replaced by uracil (U) in RNA.

**Mechanic → biology.** The player is the polymerase clamp: each template base slides into a dashed slot and must be answered with its pairing partner (correct pairs restate the hydrogen-bond count; wrong picks restate the rule). After 10 pairs the run crosses the **transcription zone** — the T button shatters into violet U, and A pairs with U from then on. Five "protein roadblock" obstacles must be jumped (real polymerases stall at DNA-binding proteins). The first 2 wrong picks are free practice; 3 slips end the run. Completing the 20-base strand shows the built mRNA sequence and a carefully worded celebration: a transcript encoding a viral protein "could be the starting blueprint for a *hypothetical* vaccine candidate — a real one also needs a cap, a tail, and years of engineering and testing."

**Objectives.** Pair any base and give its H-bond count (A–T/U: 2, G–C: 3); state the T→U substitution; describe RNA polymerase's job and what mRNA is for.

**Named simplification.** The warm-up zone pairs DNA with DNA so both pairing tables get learned — a real polymerase uses RNA rules (U) from the first base, inside a transcription bubble; directionality and speed are not modeled.

## Module 2 — Ribosome Snake (Translation)

**Concept.** The ribosome reads mRNA three bases at a time (codons), starting at AUG (Met); tRNAs deliver the matching amino acid; the chain ends when a stop codon (UAA *ochre*, UAG *amber*, UGA *opal*) is reached — stop codons bind **release factors**, not tRNAs.

**Mechanic → biology.** The snake is the growing polypeptide: the player must eat amino acids in the exact order the gene's codons specify (a new random gene each run: AUG + 8 codons + a random stop). Eating the wrong amino acid = a nonfunctional protein. Winning requires eating the release factor at the stop codon. The intro includes the start/stop codon RNA/DNA reference table.

**Objectives.** Read codons from an mRNA; explain start and stop codons by name; state that stop codons recruit release factors.

**Named simplification.** Ribosomes do not slither — movement is the game; codon→amino-acid correspondence and release-factor termination are the true part. (Real translational error rate is ~1 per 1,000–10,000 codons.)

## Module 3 — Fold-Tris (Protein folding)

**Concept.** The hydrophobic effect drives folding: hydrophobic (H) residues bury in the protein core away from water, polar (P) residues face the solvent. Misfolded proteins can aggregate (as in neurodegenerative disease); chaperones give a misfolded region another chance.

**Mechanic → biology.** A Tetris-like grid with water columns flanking a central CORE region. Pieces carry H and P residues; a row "folds" (clears) only when H residues sit in the core and P residues face water. Invalid rows lock as misfolds; three misfolds = aggregation (loss). One chaperone rescue per game. Win = six stable layers.

**Objectives.** Explain what drives folding; predict where a residue belongs; connect misfolding/aggregation to disease and say what chaperones do.

**Named simplification.** Real folding is 3D, fast, and cooperative — not falling blocks. The placement rule (H in, P out) is the true part.

## Module 4 — Phagocyte Patrol (Innate immunity & opsonization)

**Concept.** Phagocytes (macrophages, neutrophils) engulf pathogens. Encapsulated bacteria evade them until antibodies **opsonize** (tag) the pathogen — an example of innate and adaptive immunity cooperating, and of where vaccines act.

**Mechanic → biology.** A maze-chase: the player macrophage can engulf ordinary bacteria on contact, but capsuled bacteria chase the player — until an antibody pickup opsonizes them for a limited time, flipping predator and prey.

**Objectives.** Define phagocytosis and name the cells; explain opsonization; say why innate and adaptive immunity work as a team and where vaccines fit.

**Named simplification.** Macrophages don't chase through mazes, and capsules are one of several evasion tricks — the tagging-helps-eating rule is the true part.

## Module 5 — Drug Flight (Pharmacokinetics)

**Concept.** Drug concentration rises with each dose and falls with clearance (liver, kidneys). Efficacy requires staying inside the **therapeutic window**: above it is toxic, below it is ineffective — so dose timing matters.

**Mechanic → biology.** A flappy-style altitude game where height = plasma concentration. Each tap = a dose (concentration jumps up); gravity = clearance (concentration decays). TOXIC and TOO LOW bands bound the window; LIVER/KIDNEY pillars narrow it. Win = 15 dosing intervals inside the window ("steady state").

**Objectives.** Explain rise/fall of drug levels; define the therapeutic window; explain why a missed dose drops you out of the window.

**Named simplification.** Real concentrations follow smooth exponential curves, and windows differ per drug and per patient — pharmacokinetic models compute them.

## Module 6 — Lysis Lab (Antibiotics & resistance)

**Concept.** Bacteria have a peptidoglycan wall; human cells don't — the basis of **selective toxicity** for wall-targeting antibiotics (β-lactams). Resistance arises via β-lactamase; clavulanate inhibits the enzyme (the logic of co-amoxiclav).

**Mechanic → biology.** A breakout game: the wall bricks are peptidoglycan; β-lactamase bricks deflect the antibiotic ball until a clavulanate brick is hit, inhibiting the enzyme for a limited time. Clearing the wall bursts the cell by osmotic pressure (lysis).

**Objectives.** Name the wall material and why losing it bursts the cell; explain selective toxicity; describe β-lactamase and the clavulanate counter-move.

**Named simplification.** Antibiotics don't bounce — they block wall-building chemistry while the bacterium grows. The mechanism and the resistance arms race are the true part.

---

## Assessment & evidence

- Quizzes are scored client-side with a verifiable score code (deterministic hash of module + score), so instructors can validate reported scores without any account or PII.
- Planned: a shared zero-PII telemetry schema (see `TELEMETRY.md`) so aggregate play data can serve both program evaluation and a student data-analysis module.
