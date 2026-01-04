import pandas as pd
import glob
import os

def load_data(input_dir):
    """Load all datasets from input/ folder"""

    part_mds = pd.read_csv(f"{input_dir}/part_mds_sample.csv")
    machine_data = pd.read_csv(f"{input_dir}/all_machine_sample.csv")

    # Load Model BOMs
    model_files = glob.glob(f"{input_dir}/model_bom_samples/*.xlsx")
    model_boms = {}
    all_models = []
    for file in model_files:
        name = os.path.basename(file).replace("Factory_All_", "").replace("_Model_BOM.xlsx", "")
        df = pd.read_excel(file)
        df['Model'] = name
        model_boms[name] = df
        all_models.append(df)
    combined_model_bom = pd.concat(all_models, ignore_index=True)

    # Load Machine BOMs
    machine_files = glob.glob(f"{input_dir}/machine_samples/*.xlsx")
    machine_boms = {}
    all_machines = []
    for file in machine_files:
        mid = os.path.basename(file).replace("_BOM.xlsx", "")
        df = pd.read_excel(file)
        df['Machine_ID'] = mid
        machine_boms[mid] = df
        all_machines.append(df)
    combined_machine_bom = pd.concat(all_machines, ignore_index=True)

    # Summary
    print("📊 DATA LOADED:")
    print(f"  • Machine Data: {len(machine_data):,} records")
    print(f"  • Part MDS: {len(part_mds):,} records")
    print(f"  • Model BOMs: {len(combined_model_bom):,} records ({len(model_files)} files)")
    print(f"  • Machine BOMs: {len(combined_machine_bom):,} records ({len(machine_files)} files)")

    return machine_data, part_mds, model_boms, machine_boms, combined_model_bom, combined_machine_bom