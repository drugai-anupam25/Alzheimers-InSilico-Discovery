import os
import subprocess
import pandas as pd
from tqdm import tqdm

# ==========================================
# 1. TOXICITY FILTER CONFIGURATION
# ==========================================
INPUT_CSV = "ai_leads_apoe4_results.csv"           # APOE4 ke top 10 NCEs wali file
OUTPUT_CSV = "ultra_advance_molecules.csv" # Final Pass/Fail Report kahan save hogi
LIGAND_DIR = "ai_ligands_pdbqt"        # TERE LIGANDS WALA FOLDER (Agar naam alag ho to yahan change kar lena)
OUTPUT_DIR = "toxicity_docking_outputs"      # Naya folder jahan off-target logs aayenge

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Teeno targets aur unke config files
OFF_TARGETS = {
    "hERG": "config_hERG.txt",
    "CYP3A4": "config_CYP3A4.txt",
    "Pgp": "config_Pgp.txt"
}

# ==========================================
# 2. VINA EXECUTION FUNCTION
# ==========================================
def run_vina_off_target(name, target_name, config_file):
    ligand_path = os.path.join(LIGAND_DIR, f"{name}.pdbqt")
    out_pdbqt = os.path.join(OUTPUT_DIR, f"{name}_{target_name}_out.pdbqt")
    
    # Check agar ligand file miss ho gayi ho
    if not os.path.exists(ligand_path):
        print(f"  [ERROR] Ligand file nahi mili: {ligand_path}")
        return 0.0

    cmd = [
        "./vina", 
        "--config", config_file, 
        "--ligand", ligand_path,
        "--out", out_pdbqt,
        "--cpu", "8"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if line.startswith("   1 "):
                return float(line.split()[1])
    except Exception as e:
        print(f"Error docking {name} on {target_name}: {e}")
    return 0.0

# ==========================================
# 3. MAIN TOXICITY PIPELINE
# ==========================================
print("⚠️ STARTING LEVEL 1: OFF-TARGET TOXICITY FILTER ⚠️")

try:
    df = pd.read_csv(INPUT_CSV)
except FileNotFoundError:
    print(f"\n❌ ERROR: '{INPUT_CSV}' file nahi mili! Check kar le ki naam sahi hai ya nahi.")
    exit()

results_list = []

for index, row in tqdm(df.iterrows(), total=len(df), desc="Torturing Top 10 NCEs"):
    name = str(row['Name']).strip()
    apoe4_score = float(row['APOE4_Score'])
    
    print(f"\n[FIGHTING] {name} (APOE4 Target Score: {apoe4_score})")
    
    scores = {"Name": name, "APOE4_Score": apoe4_score}
    
    # Har off-target ke khilaaf dock karo
    for target_name, config_file in OFF_TARGETS.items():
        score = run_vina_off_target(name, target_name, config_file)
        scores[f"{target_name}_Score"] = score
        print(f"  -> {target_name} Target Affinity: {score} kcal/mol")
    
    # ==========================================
    # TOXICITY LOGIC (THE PASS/FAIL RULE)
    # ==========================================
    # Rule: Hum chahte hain ki off-target par binding weak (kam negative) ho.
    # Agar APOE4 score -10 hai, toh hERG/CYP score -8 se bada (-7, -6) hona chahiye safe rehne ke liye.
    
    is_herg_safe = scores["hERG_Score"] > (apoe4_score + 2.0) or scores["hERG_Score"] == 0.0
    is_cyp_safe = scores["CYP3A4_Score"] > (apoe4_score + 2.0) or scores["CYP3A4_Score"] == 0.0
    is_pgp_safe = scores["Pgp_Score"] > (apoe4_score + 1.0) or scores["Pgp_Score"] == 0.0
    
    if is_herg_safe and is_cyp_safe and is_pgp_safe:
        scores["Verdict"] = "✅ SURVIVED (IP Safe)"
        print("  => VERDICT: SAFE! 🎉")
    else:
        scores["Verdict"] = "❌ TOXIC (FAILED)"
        print("  => VERDICT: KILLED! ☠️")
        
    results_list.append(scores)

# Final matrix ko save karna
results_df = pd.DataFrame(results_list)
results_df.to_csv(OUTPUT_CSV, index=False)

print("\n=========================================")
print(f"TOXICITY SCREENING COMPLETE! Final matrix is saved to '{OUTPUT_CSV}'")