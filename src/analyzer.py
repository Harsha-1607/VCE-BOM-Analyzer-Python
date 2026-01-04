import pandas as pd

def analyze_common_parts(model_boms):
    """CASE 1: Find shared parts between models"""
    model_parts = {model: set(df['Part Number'].dropna().astype(str)) for model, df in model_boms.items()}
    models = list(model_parts.keys())

    print("📦 UNIQUE PARTS PER MODEL:")
    for model in models:
        print(f"  {model}: {len(model_parts[model]):,} parts")

    matrix = pd.DataFrame(index=models, columns=models, dtype=int)
    for m1 in models:
        for m2 in models:
            matrix.loc[m1, m2] = len(model_parts[m1] & model_parts[m2])

    print("\n📊 INTERSECTION MATRIX:")
    print(matrix)

    common_all = set.intersection(*model_parts.values())
    print(f"\n🌟 Parts in ALL models: {len(common_all):,}")

    pairs = []
    for i, m1 in enumerate(models):
        for m2 in models[i+1:]:
            shared = model_parts[m1] & model_parts[m2]
            total = min(len(model_parts[m1]), len(model_parts[m2]))
            overlap = round(len(shared) / total * 100, 1) if total else 0
            pairs.append({'Pair': f"{m1} ∩ {m2}", 'Common': len(shared), 'Overlap %': overlap})

    pair_df = pd.DataFrame(pairs)
    print("\n📋 PAIRWISE COMMON PARTS:")
    print(pair_df.to_string(index=False))

    return model_parts, matrix, pair_df, common_all


def analyze_models_across_sites(bom_data):
    """CASE 2: Which models are built at which factories?"""
    sites = bom_data['Component factory'].dropna().unique()
    models = bom_data['Model'].unique()

    presence = pd.DataFrame(index=models, columns=sites)
    for model in models:
        model_sites = bom_data[bom_data['Model'] == model]['Component factory'].dropna().unique()
        for site in sites:
            presence.loc[model, site] = '✓' if site in model_sites else '–'

    print("🏭 MODELS AT SITES (✓ = Present):")
    print(presence)

    print("\n📈 MODELS PER SITE:")
    for site in sites:
        count = (presence[site] == '✓').sum()
        print(f"  {site}: {count} models")

    print("\n📈 SITES PER MODEL:")
    for model in models:
        count = (presence.loc[model] == '✓').sum()
        print(f"  {model}: {count} sites")

    return presence


def analyze_models_across_markets(machine_data):
    """CASE 3: Where are models sold?"""
    markets = machine_data['finalMarket'].dropna().unique()
    models = machine_data['model'].dropna().unique()

    print(f"🌍 Models: {len(models)} | Markets: {len(markets)}\n")

    market_presence = pd.DataFrame(index=models, columns=sorted(markets))
    for model in models:
        model_markets = machine_data[machine_data['model'] == model]['finalMarket'].dropna().unique()
        for market in markets:
            market_presence.loc[model, market] = '✓' if market in model_markets else '–'

    market_counts = {mkt: (market_presence[mkt] == '✓').sum() for mkt in markets}
    top_markets = sorted(market_counts.items(), key=lambda x: x[1], reverse=True)[:15]

    print("📈 TOP 15 MARKETS BY MODEL COUNT:")
    for market, count in top_markets:
        print(f"  {market}: {count} models")

    return market_presence, top_markets


def analyze_mds_coverage_machine(machine_boms, part_mds):
    """CASE 4: What % of parts per machine have Accepted MDS?"""
    latest_mds = part_mds.sort_values('timestamp', ascending=False).drop_duplicates('partNumber')
    accepted = latest_mds[latest_mds['status'] == 'Accepted']
    accepted_set = set(accepted['partNumber'].astype(str))

    print(f"✅ Accepted MDS Parts: {len(accepted_set):,}\n")

    results = []
    for machine_id, bom in machine_boms.items():
        parts = bom['Part Number'].dropna().unique()
        total = len(parts)
        accepted_count = sum(1 for p in parts if str(p) in accepted_set)
        pct = round(accepted_count / total * 100, 1) if total > 0 else 0

        results.append({
            'Machine ID': machine_id,
            'Model': machine_id[:7],
            'Total Parts': total,
            'Accepted MDS': accepted_count,
            'Coverage %': pct
        })

    df = pd.DataFrame(results)
    print("📋 MDS COVERAGE BY MACHINE:")
    print(df.to_string(index=False))

    return df


def analyze_mds_coverage_model(bom_data):
    """CASE 5: Breakdown of MDS status per model"""
    statuses = bom_data['MDS Status'].unique()
    print("📋 MDS STATUSES:", [s for s in statuses if pd.notna(s)])

    counts = bom_data.groupby(['Model', 'MDS Status']).size().unstack(fill_value=0)
    pct = counts.div(counts.sum(axis=1), axis=0) * 100

    print("\n📊 COUNT BY MODEL:")
    print(counts)
    print("\n📊 % BY MODEL:")
    print(pct.round(1))

    overall = bom_data['MDS Status'].value_counts()
    print("\n📊 OVERALL:")
    for status, count in overall.items():
        pct_val = count / len(bom_data) * 100
        print(f"  {status}: {count:,} ({pct_val:.1f}%)")

    return counts, pct, overall


def analyze_annual_sales_trend(data):
    """CASE 6: Sales trend over years + top markets"""
    data['Year'] = pd.to_datetime(data['shippingDate'], errors='coerce').dt.year
    valid = data[data['Year'].notna() & (data['Year'] >= 2015)]

    annual = valid.groupby('Year').size().reset_index(name='Machines')
    print("📈 ANNUAL SALES:")
    print(annual.to_string(index=False))

    market_data = valid.groupby(['finalMarket', 'Year']).size().unstack(fill_value=0)
    market_data['Total'] = market_data.sum(axis=1)
    top_markets = market_data.sort_values('Total', ascending=False)

    print("\n📋 TOP 20 MARKETS:")
    print(top_markets.head(20))

    annual['YoY %'] = annual['Machines'].pct_change() * 100
    print("\n📈 YEAR-OVER-YEAR GROWTH:")
    print(annual.round(1).to_string(index=False))

    return annual, top_markets, valid