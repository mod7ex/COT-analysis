import os
import json
import pandas as pd
import plotly.express as px
from .constants import DATA_EXTRACTION_FOLDER_PATH, JSON_FOLDER_PATH, PICKED_MARKET, TRADERS_IN_FINANCIAL_FUTURES_FUT
from .cot import cot_all, cot_year

print_json = lambda data, i=8: print(json.dumps(data, indent=i))

# ----------------------------------------------------------------------------------------------------------------------

csv_markets_path = lambda report_type: os.path.join(DATA_EXTRACTION_FOLDER_PATH, f"{report_type}-markets.csv")

json_markets_path = lambda report_type: os.path.join(JSON_FOLDER_PATH, f"{report_type}-markets.json")

# ----------------------------------------------------------------------------------------------------------------------

report_types_cols_path = lambda report_type: os.path.join(DATA_EXTRACTION_FOLDER_PATH, f"{report_type}-report_types_cols.txt")

# ----------------------------------------------------------------------------------------------------------------------

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

# def plot_df_chart(
#         df = pd.DataFrame(),
#         chart_title: str = "Chart Title",
#         draw = True,
#         save_to_html = False,
#         save_file_name = "plot",
#         use_markers= True
# ):
#     fig = px.line(df, markers=True)

#     fig.update_layout(
#         title=chart_title,
#         template="plotly_dark",
#         paper_bgcolor="black",
#         plot_bgcolor="black",
#         # width=1500,
#         height=800,

#         # hovermode="x unified",  # one vertical hover line
#         dragmode="zoom",

#         font=dict(color="white", size=12),

#         legend=dict(
#             itemclick="toggle",        # click = hide/show
#             itemdoubleclick="toggleothers",
#             bgcolor="rgba(0,0,0,0)"
#         ),

#         xaxis=dict(
#             showgrid=True,
#             gridcolor="rgba(255,255,255,0.08)",
#             rangeslider=dict(visible=True),  # 🔥 range slider
#         ),

#         yaxis=dict(
#             title='Contracts',
#             showgrid=True,
#             gridcolor="rgba(255,255,255,0.08)",
#             fixedrange=False
#         )
#     )

#     fig.update_traces(
#         mode=f"lines{'+markers' if use_markers else ''}",
#         line=dict(width=1),
#         hovertemplate="<b>%{fullData.name}</b><br>%{y:.2f}<extra></extra>"
#     )

#     if save_to_html: fig.write_html(f"plots/{save_file_name}.html")

#     if draw: return fig.show()
#     else: return fig

def plot_df_chart(
        df = pd.DataFrame(),
        chart_title: str = "Chart Title",
        chart_type: str = "line",   # 🔥 new parameter ("line" or "bar")
        draw=True,
        save_to_html=False,
        save_file_name="plot",
        use_markers=True
):
    # 🔥 Choose chart type
    if chart_type == "line":
        fig = px.line(df, markers=use_markers)
    elif chart_type == "bar":
        fig = px.bar(df)
    else:
        raise ValueError("chart_type must be 'line' or 'bar'")

    fig.update_layout(
        title=chart_title,
        template="plotly_dark",
        paper_bgcolor="black",
        plot_bgcolor="black",
        height=800,
        dragmode="zoom",
        font=dict(color="white", size=12),
        legend=dict(
            itemclick="toggle",
            itemdoubleclick="toggleothers",
            bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
            rangeslider=dict(visible=True),  # 🔥 only for line
            # rangeslider=dict(visible=(chart_type == "line")),  # 🔥 only for line
        ),
        yaxis=dict(
            title='Contracts',
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
            fixedrange=False
        )
    )

    # 🔥 Only update traces for line charts
    if chart_type == "line":
        fig.update_traces(
            mode=f"lines{'+markers' if use_markers else ''}",
            line=dict(width=1),
            hovertemplate="<b>%{fullData.name}</b><br>%{y:.2f}<extra></extra>"
        )
    else:  # bar
        fig.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>%{y:.2f}<extra></extra>"
        )

    if save_to_html:
        fig.write_html(f"plots/{save_file_name}.html")

    if draw:
        return fig.show()
    else:
        return fig

# ----------------------------------------------------------------------------------------------------------------------

def get_market_df(cot_report_type=TRADERS_IN_FINANCIAL_FUTURES_FUT, market=PICKED_MARKET):

    df = normalize_cols(cot_all(cot_report_type=cot_report_type, verbose=True, _use_cache=True, _store=True))

    with open(json_markets_path(cot_report_type), "r") as f:
        _markets = json.load(f)

    df = df[df['cftc_contract_market_code'] == _markets[market]]

    _sig = len(df)

    # 🔎 Auto-detect date column
    date_cols = [col for col in df.columns if 'date' in col]

    if not date_cols: raise ValueError("No date column found in dataframe.")

    # take the last matching column
    df.set_index(date_cols[-1], inplace=True)

    df.index = pd.to_datetime(
        df.index,
        errors="coerce",
        format="mixed"
    )

    # drop rows where date parsing failed
    # df = df[~df.index.isna()]

    df.sort_index(inplace=True)
    df.index.name = "Date"

    if _sig != len(df): print(f"records were dropped during the date parsing step. Original: {_sig}, after parsing: {len(df)}")

    return df