import os

ROOT = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------------------------------------------------

JSON_FOLDER_NAME = 'json'

PLOTS_FOLDER_NAME = 'plots'

DATA_EXTRACTION_FOLDER_NAME = 'data'

# ----------------------------------------------------------------------------------------------------------------------

DATA_EXTRACTION_FOLDER_PATH = os.path.join(ROOT, DATA_EXTRACTION_FOLDER_NAME)

PLOTS_FOLDER_PATH = os.path.join(ROOT, PLOTS_FOLDER_NAME)

JSON_FOLDER_PATH = os.path.join(ROOT, JSON_FOLDER_NAME)

# ----------------------------------------------------------------------------------------------------------------------

csv_markets_path = lambda market: os.path.join(DATA_EXTRACTION_FOLDER_PATH, f"{market}-markets.csv")

json_markets_path = lambda market: os.path.join(JSON_FOLDER_PATH, f"{market}-markets.json")

# ----------------------------------------------------------------------------------------------------------------------

report_types_cols_path = lambda market: os.path.join(DATA_EXTRACTION_FOLDER_PATH, f"{market}-report_types_cols.txt")

# ----------------------------------------------------------------------------------------------------------------------

PICKED_MARKET = "EURO FX"