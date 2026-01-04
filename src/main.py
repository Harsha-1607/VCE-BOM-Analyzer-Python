from src.data_loader import load_data
from src.analyzer import *
from src.reporter import save_visualizations, save_reports

INPUT_DIR = "input"
OUTPUT_DIR = "output"

def main():
    print("🚀 Starting VCE BOM Analysis Pipeline...")

    # Load data
    machine_data, part_mds, model_boms, machine_boms, combined_model_bom, combined_machine_bom = load_data(INPUT_DIR)

    # --- CASE 1: Common Parts ---
    print("\n=== 🔍 CASE 1: COMMON PARTS ===")
    model_parts, matrix, pairwise_df, common_all = analyze_common_parts(model_boms)

    # --- CASE 2: Models Across Sites ---
    print("\n=== 🏭 CASE 2: SITES ===")
    presence = analyze_models_across_sites(combined_model_bom)

    # --- CASE 3: Models Across Markets ---
    print("\n=== 🌍 CASE 3: MARKETS ===")
    market_presence, top_markets = analyze_models_across_markets(machine_data)

    # --- CASE 4: MDS by Machine ---
    print("\n=== 📋 CASE 4: MDS (MACHINE) ===")
    mds_machine = analyze_mds_coverage_machine(machine_boms, part_mds)

    # --- CASE 5: MDS by Model ---
    print("\n=== 📊 CASE 5: MDS (MODEL) ===")
    mds_model, _, overall = analyze_mds_coverage_model(combined_model_bom)

    # --- CASE 6: Sales Trend ---
    print("\n=== 📈 CASE 6: SALES TREND ===")
    annual, top_markets_annual, _ = analyze_annual_sales_trend(machine_data)

    # Save outputs
    save_visualizations(OUTPUT_DIR, matrix, pairwise_df, presence, market_presence, top_markets,
                       mds_machine, mds_model, overall, annual, top_markets_annual)
    save_reports(OUTPUT_DIR, pairwise_df, presence, market_presence, mds_machine, mds_model, annual, top_markets_annual)

    # Final summary
    print("\n" + "="*50)
    print("📊 ANALYSIS SUMMARY")
    print("="*50)
    print(f"• Machines: {len(machine_data):,}")
    print(f"• Models: {machine_data['model'].nunique()}")
    print(f"• Markets: {machine_data['finalMarket'].nunique()}")
    print(f"• Model BOMs: {len(combined_model_bom):,}")
    if 'Coverage %' in mds_machine.columns:
        print(f"• Avg MDS Coverage: {mds_machine['Coverage %'].mean():.1f}%")
    print("="*50)
    print("✅ DONE — PIPELINE COMPLETE!")
    print("🏆 1st Place Volvo Data Challenge")

if __name__ == "__main__":
    main()