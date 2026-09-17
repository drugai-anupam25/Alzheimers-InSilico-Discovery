import os
import subprocess
import pandas as pd
from tqdm import tqdm

# ==========================================
# 1. AI PIPELINE CONFIGURATION
# ==========================================
INPUT_CSV = "leads.csv"                     # TERA NAYA CSV FILE
OUTPUT_CSV = "ai_leads_apoe4_results.csv"   # Final APOE4 scores kahan save honge
LIGAND_DIR = "ai_ligands_pdbqt"             # Naye 3D ligands ka folder
OUT_DIR = "ai_docking_outputs"              # Vina ke outputs ka folder
APOE4_CONFIG = "config.txt"                 # TERA APOE4 KA CONFIG FILE (Naam check kar lena!)

os.makedirs(LIGAND_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

# ==========================================
# 2. MASTER FUNCTION (SMILES -> 3D -> DOCK)
# ==========================================
def process_and_dock(name, smiles):
    pdbqt_path = os.path.join(LIGAND_DIR, f"{name}.pdbqt")
    out_pdbqt = os.path.join(OUT_DIR, f"{name}_out.pdbqt")
    
    # --- PHASE 1: OpenBabel (SMILES to 3D PDBQT with pH 7.4) ---
    # --gen3d = 3D structure, -h = Add Hydrogens, -p 7.4 = Protonation state in blood
    obabel_cmd = f'obabel -:"{smiles}" -O "{pdbqt_path}" --gen3d -h -p 7.4'
    
    try:
        subprocess.run(obabel_cmd, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except Exception as e:
        print(f"  [ERROR] OpenBabel fail hua {name} ke liye: {e}")
        return 0.0
        
    if not os.path.exists(pdbqt_path):
        print(f"  [ERROR] {name}.pdbqt generate nahi hua!")
        return 0.0

    # --- PHASE 2: AutoDock Vina (Targetting APOE4) ---
    vina_cmd = [
        "./vina", 
        "--config", APOE4_CONFIG, 
        "--ligand", pdbqt_path,
        "--out", out_pdbqt,
        "--cpu", "8"
    ]
    
    try:
        result = subprocess.run(vina_cmd, capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if line.startswith("   1 "):  # Mode 1 ki affinity pakadna
                return float(line.split()[1])
    except Exception as e:
        print(f"  [ERROR] Vina fail hua {name} ke liye: {e}")
    
    return 0.0

# ==========================================
# 3. RUN THE PIPELINE
# ==========================================
print("🚀 STARTING NEXT-GEN AI DOCKING PIPELINE 🚀")

try:
    df = pd.read_csv(INPUT_CSV)
except FileNotFoundError:
    print(f"\n❌ ERROR: '{INPUT_CSV}' file nahi mili!")
    exit()

results_list = []

for index, row in tqdm(df.iterrows(), total=len(df), desc="Docking AI Leads"):
    name = str(row['Name']).strip()
    smiles = str(row['SMILES']).strip()
    
    print(f"\n[OPTIMIZING & DOCKING] {name}...")
    score = process_and_dock(name, smiles)
    print(f"  -> APOE4 Affinity: {score} kcal/mol")
    
    results_list.append({
        "Name": name,
        "SMILES": smiles,
        "APOE4_Score": score
    })

# Save Final Results
results_df = pd.DataFrame(results_list)
results_df = results_df.sort_values(by="APOE4_Score", ascending=True) # Best score sabse upar
results_df.to_csv(OUTPUT_CSV, index=False)

print("\n=========================================")
print(f"🔥 MISSION ACCOMPLISHED! Results saved in '{OUTPUT_CSV}' 🔥")