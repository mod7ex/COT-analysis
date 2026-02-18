from utils.cot import cot_all, TRADERS_IN_FINANCIAL_FUTURES_FUT
from utils.index import normalize_cols
import pandas as pd
import json
from config import PICKED_MARKET, json_markets_path

def get_market_df(cot_report_type=TRADERS_IN_FINANCIAL_FUTURES_FUT, market=PICKED_MARKET):

    df = normalize_cols(cot_all( cot_report_type=cot_report_type, verbose=True, _use_cache=True, _store=True))

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