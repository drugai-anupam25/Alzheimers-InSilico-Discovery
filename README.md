# APOE4 Alzheimer's Drug Discovery: In-Silico Lead Optimization & Toxicity Pipeline

**Author:** Computational Biologist / Aging Researcher (Lucknow University)
**Hardware Environment:** Apple Silicon (M4 MacBook Air)
**Target:** APOE4 Receptor (Alzheimer's Disease)

## 📌 Project Overview
This repository contains an automated, end-to-end computational drug discovery pipeline targeting the APOE4 protein. The core objective was to move away from random high-throughput screening (HTS) and implement high-quality, rationally designed chemical surgeries to develop New Chemical Entities (NCEs). 

Crucially, this project documents **The Lead Optimization Paradox**—demonstrating how high-affinity APOE4 binders fail catastrophic safety checks (hERG/CYP3A4), and why documenting these failures is vital for open science.

---

## 🔬 The Approach: 5 "God-Tier" Chemical Surgeries
Instead of adding random lipophilic or halogenated groups (which increase toxicity), we designed 25 targeted variants from highly toxic parent scaffolds (DKP, Tetrahydro-beta-carboline, Tadalafil, Tricyclic) using 5 distinct rational strategies:

1. **Ghost Drug (Prodrug):** Masked toxic basic amines with polar locks (e.g., Glycinamide) that only cleave upon crossing the BBB.
2. **Trojan Horse (LAT1 Mimic):** Engineered zwitterionic appendages to exploit the brain's LAT1 active transporter while repelling off-target binding.
3. **Arg-112 Wedge (Mutation Sniper):** Substituted flat aromatic rings with ultra-polar bioisosteres (Tetrazole) to specifically target the APOE4 Arg112-Glu109 salt bridge.
4. **Water-Bridge Binder:** Swapped flat 2D phenyls for 3D sp3-rich oxygenated rings (THP) to escape flat hERG pockets and bond with trapped water in APOE4.
5. **The Minimalist:** Drastically reduced molecular weight to maximize Ligand Efficiency (LE) and avoid bulky hydrophobic clashes.

---

## ⚙️ The Automation Pipeline
The workflow is fully automated via Python scripts bridging 1D SMILES to 3D docking:

* **`sanjeevaninewdock.py`**: Reads `leads.csv`, automatically converts SMILES to 3D PDBQT using OpenBabel (set strictly to physiological pH 7.4), and executes AutoDock Vina targeting APOE4.
* **`toxicity_filter.py` ("The Cross-Docking Filter"):** The safety checkpoint. It takes the top APOE4 hits and cross-docks them against three critical off-targets:
  * **hERG (5VA1):** Cardiotoxicity (QT prolongation).
  * **CYP3A4:** Liver metabolism / Rapid clearance.
  * **P-glycoprotein (6QEX):** BBB efflux pump.

---

## ❌ The Results & Why We Failed (Documenting Negative Data)
Despite achieving phenomenal binding affinities with our optimized leads (e.g., `DKP1_THP` achieved an APOE4 score of **-9.964 kcal/mol**), the pipeline highlighted a brutal reality of drug design: **The Core Scaffold Trap.**

When the top 11 APOE4 champions were fed into the `toxicity_filter.py`, they were almost uniformly **KILLED** by the off-target checks. 
* **Example Failure:** `DKP1_THP` scored **-13.08 kcal/mol on hERG** and **-9.861 on CYP3A4**. 
* **The Root Cause:** While our peripheral chemical surgeries (THP, polar locks) were sound, the *parent skeletons* (DKP, Tadalafil cores) are inherently massive, flat, and hydrophobic. The hERG potassium channel possesses a massive hydrophobic vacuum that acts as a magnet for these large scaffolds. AutoDock Vina algorithmically over-scores these large lipophilic cores in the hERG pocket, overriding the protective peripheral modifications.

**Conclusion:** Modifying the edges of a fundamentally toxic, flat synthetic core is insufficient. The parent scaffold itself must have high sp3 character and low lipophilicity.

---

## 🚀 Next Steps: The Pivot to Nature
Having proven that traditional synthetic cores easily fall into the hERG/CYP trap, our next phase abandons these synthetic structures entirely. We are pivoting the pipeline to screen a **Raw Ayurvedic/Natural Compound Library**. Natural products inherently possess complex 3D (sp3-rich) architectures, offering built-in protection against flat hERG and CYP3A4 pockets while maintaining high BBB permeability.

---
*Dedicated to transparent, open-source aging research.*
