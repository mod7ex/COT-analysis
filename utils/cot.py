import os
import pandas as pd
import requests, zipfile, io
from datetime import date
import json
from pathlib import Path
from config import ROOT, DATA_EXTRACTION_FOLDER_PATH

BASE_URL = "https://cftc.gov/files/dea/history/"

LEGUACY_FUT = 'legacy_fut'
LEGACY_FUTOPT = 'legacy_futopt'
SUPPLEMENTAL_FUTOPT = 'supplemental_futopt'
DISAGGREGATED_FUT = 'disaggregated_fut'
DISAGGREGATED_FUTOPT = 'disaggregated_futopt'
TRADERS_IN_FINANCIAL_FUTURES_FUT = 'traders_in_financial_futures_fut'
TRADERS_IN_FINANCIAL_FUTURES_FUTOPT = 'traders_in_financial_futures_futopt'

with open(os.path.join(ROOT, "utils", "cot.json"), "r") as f:
   REPORT_TYPES = json.load(f)

# --------------------------------------------------------------------------------------------------------------------

# def fetch_data(_url):
#    os.makedirs(DATA_EXTRACTION_FOLDER_NAME, exist_ok=True)

#    _req = requests.get(_url)
#    z = zipfile.ZipFile(io.BytesIO(_req.content))
#    z.extractall(path=DATA_EXTRACTION_FOLDER_PATH)
#    _file_name = z.namelist()[0]
#    _file_path = os.path.join(DATA_EXTRACTION_FOLDER_NAME, _file_name)
#    df = pd.read_csv(_file_path, low_memory=False)

#    os.remove(_file_path)

#    return df

# --------------------------------------------------------------------------------------------------------------------

def fetch_data(_identifier, _store = False, _use_cache = False):
   _file_path = os.path.join(DATA_EXTRACTION_FOLDER_PATH, f"{_identifier}.csv")

   if _use_cache:
      _path = Path(_file_path)

      if _path.exists():
         return pd.read_csv(_file_path, low_memory=False)

   response = requests.get(BASE_URL + _identifier + ".zip")
   response.raise_for_status()

   with zipfile.ZipFile(io.BytesIO(response.content)) as z:
      _csv_name = z.namelist()[0] # assume the zip contains exactly one CSV

      with z.open(_csv_name) as csv_file:
         df = pd.read_csv(csv_file, low_memory=False)
   
   if _store:
      if not os.path.isdir(DATA_EXTRACTION_FOLDER_PATH):
         os.makedirs(DATA_EXTRACTION_FOLDER_PATH, exist_ok=True)
      df.to_csv(_file_path, index=False)

   return df

# --------------------------------------------------------------------------------------------------------------------

def cot_hist(cot_report_type = LEGUACY_FUT, _use_cache = False, _store = False, verbose=True):

   if cot_report_type in REPORT_TYPES:
      url_end = REPORT_TYPES[cot_report_type]['hist']['url_end']
      # txt = REPORT_TYPES[cot_report_type]['hist']['txt']
      if verbose: print(f"Selected: {REPORT_TYPES[cot_report_type]['description']} - loading historical data ...")
      return fetch_data(str(url_end), _store=_store, _use_cache=_use_cache)
   else:
      raise  ValueError("Input needs to be either: " + ", ".join(REPORT_TYPES.keys()))
   
# --------------------------------------------------------------------------------------------------------------------

def cot_year(year = date.today().year, cot_report_type = LEGUACY_FUT, _use_cache = False, _store = False, verbose=True):

   if cot_report_type in REPORT_TYPES:
      rep = REPORT_TYPES[cot_report_type]['year']['rep']
      # txt = REPORT_TYPES[cot_report_type]['year']['txt']
      if verbose: print(f"Selected: {REPORT_TYPES[cot_report_type]['description']} from year: {year} - loading data ...")
      return fetch_data(rep + str(year), _store = _store, _use_cache = _use_cache)
   else:
      raise  ValueError("Input needs to be either: " + ", ".join(REPORT_TYPES.keys()))

# --------------------------------------------------------------------------------------------------------------------

def cot_all(cot_report_type = LEGUACY_FUT, verbose=True, _store = False, _use_cache = False): 
   if verbose: print(f"loading data for the report type: {cot_report_type} ...")

   return pd.concat([
      cot_hist(cot_report_type, verbose=verbose, _store=_store, _use_cache=_use_cache), # Get historical data till 2016 (included)  
      pd.concat([cot_year(i, cot_report_type, verbose=verbose, _store=_store, _use_cache=_use_cache) for i in range(2017, date.today().year+1)])
   ])

# --------------------------------------------------------------------------------------------------------------------