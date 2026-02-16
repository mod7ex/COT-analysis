import plotly.express as px
from pandas import DataFrame
from .cot import cot_year
from config import report_types_cols_path
import json
from config import csv_markets_path, json_markets_path

def get_markets(cot_report_type, save_csv=False, save_json=False):
    df = cot_year(cot_report_type=cot_report_type, verbose=True, _use_cache=True, _store=False)

    df = df[['CFTC_Contract_Market_Code', 'Market_and_Exchange_Names']]

    df.columns = ["Market_Code", "Market_Name"]

    df.drop_duplicates(subset=["Market_Code"], keep="last")

    # Save as csv
    if save_csv: df.to_csv(csv_markets_path(cot_report_type))

    # Save as json
    if save_json:
        with open(json_markets_path(cot_report_type), "w") as f:
            json.dump(dict(zip(df["Market_Name"], df["Market_Code"])), f, indent=4)

    return df

def get_report_type_cols(cot_report_type, save=False):
    df = cot_year(cot_report_type=cot_report_type, verbose=True, _use_cache=True, _store=False)
    
    for i, col in enumerate(df.columns, 1):
        print(f"| {i} | {col} |")

    if save:
        with open(report_types_cols_path(cot_report_type), "w") as f:
            for col in df.columns:
                f.write(col + "\n")

def plot_df_line_chart(
        df = DataFrame(),
        chart_title: str = "Chart Title",
        draw = True,
        save_to_html = False,
        save_file_name = "plot",
        use_markers= True
):
    fig = px.line(df, markers=True)

    fig.update_layout(
        title=chart_title,
        template="plotly_dark",
        paper_bgcolor="black",
        plot_bgcolor="black",
        # width=1500,
        height=800,

        # hovermode="x unified",  # one vertical hover line
        dragmode="zoom",

        font=dict(color="white", size=12),

        legend=dict(
            itemclick="toggle",        # click = hide/show
            itemdoubleclick="toggleothers",
            bgcolor="rgba(0,0,0,0)"
        ),

        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
            rangeslider=dict(visible=True),  # 🔥 range slider
        ),

        yaxis=dict(
            title='Contracts',
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
            fixedrange=False
        )
    )

    fig.update_traces(
        mode=f"lines{'+markers' if use_markers else ''}",
        line=dict(width=1),
        hovertemplate="<b>%{fullData.name}</b><br>%{y:.2f}<extra></extra>"
    )

    if save_to_html: fig.write_html(f"plots/{save_file_name}.html")

    if draw: return fig.show()
    else: return fig