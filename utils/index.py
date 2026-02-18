import json
from .cot import cot_year
from pandas import DataFrame
import plotly.express as px
from config import report_types_cols_path
from config import csv_markets_path, json_markets_path

def normalize_col(col: str):
    return (
        col
        .strip()
        .lower()
        .replace("-", "_")
        .replace("--", "_")
        .replace("__", "_")
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
    )

def normalize_cols(df):
    df.columns = [normalize_col(col.strip()) for col in df.columns]
    return df

def get_markets(cot_report_type, save_csv=False, save_json=False):
    # Normalize column names
    df = normalize_cols(cot_year(
        cot_report_type=cot_report_type,
        verbose=True,
        _use_cache=True,
        _store=False
    ))

    # Now we use standardized column names
    df = df[['cftc_contract_market_code', 'market_and_exchange_names']]

    df.columns = ["market_code", "market_name"]

    df['market_name'] = df['market_name'].str.split(' - ').str[0]

    df.drop_duplicates(subset=["market_code"], keep="last", inplace=True)

    if save_csv:
        df.to_csv(csv_markets_path(cot_report_type), index=False)

    if save_json:
        with open(json_markets_path(cot_report_type), "w") as f:
            json.dump(dict(zip(df["market_name"], df["market_code"])), f, indent=4)

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