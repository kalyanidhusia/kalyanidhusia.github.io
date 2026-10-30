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

## Module 7 — Alignment Grid (Needleman–Wunsch global alignment)

**Concept.** The optimal end-to-end (global) alignment of two sequences falls out of a dynamic-programming matrix: each cell holds the best score for aligning the prefixes ending there, computed as the maximum over three finished neighbors — diagonal (pair the letters: match/mismatch), above and left (gaps). The traceback through the winning arrows reconstructs the alignment itself.

**Mechanic → biology/CS.** The DP grid is the game board. For each cell the player is shown the three candidate scores and must tap the maximum — the recurrence, executed by hand. Filling the full matrix unlocks the traceback phase: from the bottom-right corner the player taps, cell by cell, the move each value came from, and the alignment assembles letter by letter on the win screen. Two free practice slips, then three slips end the run.

**Objectives.** State what one matrix cell means and name its three sources; distinguish the diagonal move (pairing) from gap moves; explain what the traceback recovers and why NW is exact and global — with Smith–Waterman as the exact local counterpart and BLASTP as the fast heuristic (never "NW inside BLASTP").

**Named simplification.** Training-wheel scoring (match +2, mismatch −1, gap −2) keeps the arithmetic mental; real protein alignment uses BLOSUM62 and affine gaps. The table, the max-of-three rule, and the traceback are the true parts.

## Module 8 — Seed & Extend (BLASTP heuristic local search)

**Concept.** BLASTP trades guaranteed-best for speed: it only aligns where a short query word (3 amino acids for proteins) matches — a seed — then extends the hit outward while the score holds, and skips seedless sequences entirely. The E-value converts a hit score into "expected chance hits this good in a database this size."

**Mechanic → biology/CS.** Three database sequences, one query with its seed word highlighted. The player must (1) tap where the seed sits — or press Skip when no seed exists, the round whose correct move IS the heuristic's defining shortcut; (2) extend the hit left/right with the running score visible; (3) stop at the peak — the X-drop intuition. The win screen is a BLASTP-style hit report ranking the three outcomes, including the skip.

**Objectives.** Explain seeding and the cost of skipping seedless sequences; describe extension as growing a local alignment that stops when the score decays; give the E-value idea at intuition level; name Smith–Waterman as the exact local algorithm BLAST approximates.

**Named simplification.** Real BLASTP seeds on BLOSUM62 "neighborhood words" (near-matches count), uses two-hit triggers and X-drop extension, and computes E-values from Karlin–Altschul statistics. Exact-match seeds, +2/−1 scoring, and stop-at-the-peak are the training-wheel versions.

**The pair is scientifically distinct on purpose.** Module 7 is the exact, global, guaranteed algorithm; Module 8 is the fast, heuristic, local search. Playing them back-to-back is a lesson in algorithmic trade-offs — the sensibility the program wants computing students to bring into biology.

## Module 9 — Genome Builder (De Bruijn assembly)

**Concept.** Assemblers chop short reads into k-mers and link k−1 overlaps into a De Bruijn graph; walking the graph rebuilds the genome. Repeats make the graph branch with equal read support — information the short reads simply do not contain — and sequencing errors appear as barely supported dead-end tips that assemblers prune.

**Mechanic → biology/CS.** The k-mer walk is the game. The contig grows one base per correct k-mer tap (the overlap rule enforced every step), with read support shown on every candidate. Round 1 is a clean walk; round 2 contains a repeat — two equally supported branches, where the only correct move is the **Ambiguous** button (guessing is a slip by design), after which a longer read arrives and resolves the branch; round 3 contains a 1-read error tip, where coverage breaks the tie and picking the weak branch is a slip. Two free practice slips, then three slips end the run.

**Objectives.** Define a k-mer and the k−1 overlap; recognize repeat ambiguity and say what resolves it (longer reads / mate pairs); recognize an error tip and say what assemblers do with it.

**Named simplification.** k-mers are walked as nodes joined by k−1 overlaps; the textbook De Bruijn formulation makes k-mers the edges between (k−1)-mer nodes and finds an Eulerian path. Real assemblers use k ≈ 31–77 over millions of reads, prune tips and pop bubbles statistically, and never know the true genome in advance (here it referees the taps).

## Module 10 — Variant Detective (variant calling as evidence weighing)

**Concept.** A mismatch in aligned reads is a hypothesis, not a mutation. Callers weigh base quality, mapping quality, strand balance, and sequence context — and when depth is too thin to decide, the honest verdict is *unresolved*. Detecting a real variant is, separately, not evidence that it causes disease.

**Mechanic → biology/CS.** Five read pileups, each with a highlighted candidate site and an **evidence budget of 2 checks** — the budget forces the player to reason about which evidence discriminates for this case. Verdict buttons: Real / Artifact / Unresolved, with Unresolved as a scoring answer (the thin-pile case). Two cases carry identical alt-read counts and opposite verdicts (clean het vs. MAPQ-0 mismapping), making the don't-trust-raw-counts lesson structural. Wrong verdicts reveal all four evidence lines; one practice verdict, then three slips end the shift.

**Objectives.** Name the four evidence types and what each rules in or out; explain why identical counts can deserve opposite verdicts; state that detection and pathogenicity are separate questions with separate evidence standards.

**Named simplification.** Real callers integrate all evidence probabilistically (per-base and per-read qualities → genotype likelihoods) rather than spending a 2-check budget, and hard cases are settled by orthogonal validation, not a verdict button. The evidence types, the artifact signatures, and unresolved-as-an-answer are the true parts.

## Module 11 — Leakage Lab (honest ML evaluation)

**Concept.** Data leakage — any crack that lets test information reach training — silently inflates accuracy. The classics in biomedicine: the same patient on both sides of the split, preprocessing fit on all data before splitting, and feature selection performed on the full dataset. Leaky pipelines ace cross-validation and collapse on genuinely unseen data.

**Mechanic → biology/CS.** Ten patient visits stream one at a time into Train/Test bins: repeat visits must follow their patient (splitting a patient is a slip, with the model-recognizes-the-person explanation), and at least two patients must be held out. Two pipeline decisions follow (scaler fit, feature selection), each with one honest option. The reveal draws the player's clean pipeline next to its leaky twin — CV 87/holdout 84 versus CV 96/holdout 61 — so the collapse *is* the diagnosis, then a final judgment round asks which reported number deserves trust (answer: none, until the evaluation is redone clean). Two practice slips, then three slips void the evaluation.

**Objectives.** Split by patient (and by site when the claim demands it); order preprocessing and selection inside training data; read a results table with suspicion and say which number to trust.

**Named simplification.** Accuracy numbers are illustrative, not computed from a live model; two hospitals stand in for the full zoo of site/batch effects; real leakage is sneakier (temporal leakage, label proxies, duplicates). The three sealed cracks are the most common real ones, per the scikit-learn pitfalls documentation.

## Module 12 — Pipeline Rescue (reproducible workflows)

**Concept.** Analyses are DAGs of tasks wired by their inputs. The wiring is what lets workflow engines resume after a crash or a change: unchanged inputs → cached, valid results; anything downstream of a change → stale, must rerun. Root cause and crash site are different places, and pipelines usually die of metadata (sample IDs, reference versions), not code.

**Mechanic → biology/CS.** The player wires the DAG (each task's true inputs), then survives two failures: a samplesheet/BAM sample-ID mismatch (root cause lives two tasks upstream of the crash; blaming the crash site is a slip) and a reference-genome update. Each rescue requires queuing **exactly** the stale task set — queuing a cached task is a slip that names the wasted CPU-hours, resuming without a stale task is a slip that names the wrong-results risk — and valid cached tasks bank CPU-hours in the HUD. The win screen is a run record: inputs, versions, what reran — provenance as the prize. Two practice slips, then three slips kill the run.

**Objectives.** Wire tasks to their real inputs; separate root cause from crash site; name the stale set and the cached set after any change; say what a run record is for.

**Named simplification.** Real engines (Nextflow, Snakemake) decide staleness by hashing file contents, parameters, code, and container versions — not by trusting taps — and real failures arrive with schedulers, retries, and memory limits attached. Four tasks stand in for pipelines that run hundreds.

**The second pair is a deliberate arc.** Modules 9–10 extend the algorithmic story (align → assemble → call) that recruits computing students into biology; Modules 11–12 are research readiness — the evaluation discipline and computational hygiene students need before contributing to a real project.

## Research frontiers (Modules 13+)

This section hosts modules whose concepts come from **active research programs**: a researcher contributes the concept and the scientific sign-off; the arcade contributes the module loop, the framework, and the honesty rules. The section exists to be added to — any teachable research concept with a mechanic inside it is a candidate. The same loop, quiz contract, and named-simplifications requirement apply without exception.

## Module 13 — Chromatin Command (cardiovascular epigenetics: the acetylation switch)

**Concept.** Heart cells tune gene activity with reversible acetyl marks on histone tails: writers (HATs) add marks and open chromatin for transcription, erasers (HDACs) remove them and silence it, readers (e.g., BRD4) couple marks to the transcription machinery. The acetyl groups come from acetyl-CoA, wiring metabolism directly into gene regulation — the axis that makes HDAC inhibitors (e.g., SAHA/vorinostat) candidate cardiometabolic therapeutics, and the reason they are double-edged: blocking the erasers de-represses everything they were holding shut.

**Mechanic → biology.** A fixed-shooter where the player IS the HAT writer: firing an acetyl mark (spending a regenerating acetyl-CoA budget — metabolism as ammunition) opens a gene gate, and the player can only open, never close. Protective adult-program genes (SERCA2a, MYH6, RYR2, PGC-1α, CPT1B) score when transcribed; fetal stress-program genes (NPPA, NPPB, MYH7) damage the heart when transcribed. HDAC ships close any gate they cross — rendered as regulators, not villains, because they are the only mechanism that can close a stress gate opened by mistake. The SAHA blockade freezes every eraser and locks all gates: the ultimate defense for protective genes that simultaneously locks open any leaking stress gate — the drug's indiscriminate de-repression experienced inside the mechanic. First 2 mistakes are free practice; survive 10 polymerase waves.

**Objectives.** Name writer/eraser/reader (HAT, HDAC, BRD4) and what each does; state what acetylation does to chromatin and transcription; explain why an HDAC inhibitor raises expression of helpful and harmful genes alike; connect acetyl-CoA supply to epigenetic regulation.

**Named simplifications.** Real chromatin is 3D with dozens of modifiable residues and locus-specific targeting, not eight binary gates; HDACs span four classes with different (often non-histone) substrates, and no drug inhibits all of them equally or in five-second pulses; "protective vs. stress" is the adult-vs-fetal gene program as a teaching split; polymerase is recruited by readers and transcription factors, not dive-bombing. The true parts: acetylation is reversible, writer/eraser balance sets gene output, the marks are paid for in acetyl-CoA, and eraser inhibition de-represses indiscriminately.

---

## Assessment & evidence

- Quizzes are scored client-side with a verifiable score code (deterministic hash of module + score), so instructors can validate reported scores without any account or PII.
- Planned: a shared zero-PII telemetry schema (see `TELEMETRY.md`) so aggregate play data can serve both program evaluation and a student data-analysis module.
