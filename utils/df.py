from utils.cot import cot_all, TRADERS_IN_FINANCIAL_FUTURES_FUT
import pandas as pd
import json
from config import PICKED_MARKET, json_markets_path

def get_market_df(cot_report_type=TRADERS_IN_FINANCIAL_FUTURES_FUT, market=PICKED_MARKET):
    df = cot_all(cot_report_type=cot_report_type, verbose=True, _use_cache=True, _store=True)

    with open(json_markets_path(cot_report_type), "r") as f:
        _markets = json.load(f)

    _filter = df['CFTC_Contract_Market_Code'] == _markets[market]

    df = df[_filter]

    _sig = len(df)

    df.set_index('Report_Date_as_YYYY-MM-DD', inplace=True)

    df.index = pd.to_datetime(
        df.index,
        errors="coerce",
        format="mixed"
    )

    df.sort_index(inplace=True)

    df.index.name = 'Date'

    if _sig != len(df): print(f"records were dropped during the date parsing step. Original: {_sig}, after parsing: {len(df)}")

    return df