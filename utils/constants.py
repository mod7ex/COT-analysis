import os
# import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# sys.path.insert(0, ROOT)

# ----------------------------------------------------------------------------------------------------------------------

JSON_FOLDER_NAME = 'json'

PLOTS_FOLDER_NAME = 'plots'

DATA_EXTRACTION_FOLDER_NAME = 'data'

# ----------------------------------------------------------------------------------------------------------------------

DATA_EXTRACTION_FOLDER_PATH = os.path.join(ROOT, DATA_EXTRACTION_FOLDER_NAME)

PLOTS_FOLDER_PATH = os.path.join(ROOT, PLOTS_FOLDER_NAME)

JSON_FOLDER_PATH = os.path.join(ROOT, JSON_FOLDER_NAME)

# ----------------------------------------------------------------------------------------------------------------------

PICKED_MARKET = "EURO FX"

# ----------------------------------------------------------------------------------------------------------------------

BASE_URL = "https://cftc.gov/files/dea/history/"

# COT Report Types
LEGUACY_FUT = 'legacy_fut'
LEGACY_FUTOPT = 'legacy_futopt'
SUPPLEMENTAL_FUTOPT = 'supplemental_futopt'
DISAGGREGATED_FUT = 'disaggregated_fut'
DISAGGREGATED_FUTOPT = 'disaggregated_futopt'
TRADERS_IN_FINANCIAL_FUTURES_FUT = 'traders_in_financial_futures_fut'
TRADERS_IN_FINANCIAL_FUTURES_FUTOPT = 'traders_in_financial_futures_futopt'

# ----------------------------------------------------------------------------------------------------------------------