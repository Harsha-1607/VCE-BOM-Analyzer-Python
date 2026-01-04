import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

def save_visualizations(output_dir,
                       intersection_matrix=None, pairwise_df=None,
                       presence=None, market_presence=None, sorted_markets=None,
                       machine_mds_df=None, model_mds=None, overall=None,
                       annual=None, market_sorted=None):
    """Save all charts as PNGs"""
    out = Path(output_dir)
    out.mkdir(exist_ok=True)

    try:
        # 1. Common Parts Matrix
        if intersection_matrix is not None:
            fig = px.imshow(intersection_matrix.astype(int), text_auto=True,
                            title="🔧 Common Parts Matrix", color_continuous_scale="Blues")
            fig.update_layout(width=700, height=500)
            fig.write_image(out / "common_parts_heatmap.png")

        # 2. Pairwise Comparison
        if pairwise_df is not None:
            fig = px.bar(pairwise_df, x='Pair', y='Common', color='Overlap %', text='Common',
                         title="🔗 Common Parts Between Model Pairs", color_continuous_scale='Viridis')
            fig.update_layout(width=850, height=400)
            fig.write_image(out / "pairwise_common_parts.png")

        # 3. Models Across Sites
        if presence is not None:
            num = presence.replace({'✓': 1, '–': 0}).astype(int)
            fig = go.Figure(go.Heatmap(
                z=num.values, x=num.columns, y=num.index,
                text=presence.values, texttemplate="%{text}", textfont_size=14,
                colorscale=[[0, 'white'], [1, '#90EE90']], showscale=False, xgap=3, ygap=3
            ))
            fig.update_layout(title="🏭 Models Across Sites", width=1100, height=450,
                              xaxis_tickangle=-45, yaxis_autorange='reversed')
            fig.write_image(out / "models_across_sites.png")

        # 4. Models Across Markets (Top 20)
        if market_presence is not None and sorted_markets:
            top_names = [m[0] for m in sorted_markets[:20]]
            if top_names:
                top_data = market_presence[top_names]
                num = top_data.replace({'✓': 1, '–': 0}).astype(int)
                fig = go.Figure(go.Heatmap(
                    z=num.values, x=num.columns, y=num.index,
                    text=top_data.values, texttemplate="%{text}", textfont_size=12,
                    colorscale=[[0, 'white'], [1, '#87CEEB']], showscale=False, xgap=3, ygap=3
                ))
                fig.update_layout(title="🌍 Models Across Top 20 Markets", width=1100, height=400,
                                  xaxis_tickangle=-45, yaxis_autorange='reversed')
                fig.write_image(out / "models_across_markets.png")

        # 5. MDS Coverage by Machine
        if machine_mds_df is not None:
            df_sorted = machine_mds_df.sort_values('Coverage %', ascending=False)
            fig = px.bar(df_sorted, x='Machine ID', y='Coverage %', color='Model',
                         title="📋 MDS Coverage by Machine", hover_data=['Total Parts', 'Accepted MDS'])
            avg = df_sorted['Coverage %'].mean()
            fig.add_hline(y=avg, line_dash="dash", annotation_text=f"Avg: {avg:.1f}%")
            fig.update_layout(width=1000, height=400, xaxis_tickangle=-45)
            fig.write_image(out / "mds_by_machine.png")

        # 6. Overall MDS Status
        if overall is not None:
            fig = px.pie(values=overall.values, names=overall.index,
                         title="📊 Overall MDS Distribution", hole=0.4)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(width=700, height=550)
            fig.write_image(out / "mds_overall_pie.png")

        # 7. Annual Sales Trend
        if annual is not None:
            fig = px.line(annual, x='Year', y='Machines', markers=True,
                          title="📈 Annual Sales Trend")
            fig.update_traces(line_width=3, marker_size=10)
            fig.update_layout(width=850, height=400)
            fig.write_image(out / "annual_sales_trend.png")

        # 8. Top Markets Trend
        if market_sorted is not None:
            top10 = market_sorted.head(10).drop(columns='Total').reset_index()
            melted = top10.melt(id_vars='finalMarket', var_name='Year', value_name='Machines Sold')
            fig = px.line(melted, x='Year', y='Machines Sold', color='finalMarket', markers=True,
                          title="📈 Top 10 Markets Trend")
            fig.update_layout(width=950, height=450)
            fig.write_image(out / "top_markets_trend.png")

        print(f"✅ Charts saved to {output_dir}")

    except Exception as e:
        print(f"⚠️  Chart save failed: {e}")


def save_reports(output_dir,
                pairwise_df=None, presence=None, market_presence=None,
                machine_mds_df=None, model_mds=None, annual=None, market_sorted=None):
    """Save reports as Excel files"""
    out = Path(output_dir)
    out.mkdir(exist_ok=True)

    try:
        if pairwise_df is not None:
            pairwise_df.to_excel(out / "report_pairwise_common_parts.xlsx", index=False)
        if presence is not None:
            presence.to_excel(out / "report_models_across_sites.xlsx")
        if market_presence is not None:
            market_presence.to_excel(out / "report_models_across_markets.xlsx")
        if machine_mds_df is not None:
            machine_mds_df.to_excel(out / "report_mds_by_machine.xlsx", index=False)
        if model_mds is not None:
            model_mds.to_excel(out / "report_mds_by_model.xlsx")
        if annual is not None:
            annual.to_excel(out / "report_annual_sales.xlsx", index=False)
        if market_sorted is not None:
            market_sorted.to_excel(out / "report_top_markets.xlsx")

        print(f"📊 Reports saved to {output_dir}")
    except Exception as e:
        print(f"⚠️  Report save failed: {e}")