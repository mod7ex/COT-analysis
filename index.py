import os
import pandas as pd
import requests, zipfile, io
from datetime import date
from bs4 import BeautifulSoup

# COT report types:  
#   "legacy_fut" as report type argument selects the Legacy futures only report,
#   "legacy_futopt" the Legacy futures and options report,
#   "supplemental_futopt" the Sumpplemental futures and options reports,
#   "disaggregated_fut" the Disaggregated futures only report, 
#   "disaggregated_futopt" the COT Disaggregated futures and options report, 
#   "traders_in_financial_futures_fut" the Traders in Financial Futures futures only report, and 
#   "traders_in_financial_futures_fut" the Traders in Financial Futures futures and options report. 

EXTRACTION_FOLDER_NAME = 'data'
PLOTS_FOLDER_NAME = 'plots'

EXTRACTION_FOLDER_PATH = os.path.join(os.getcwd(), EXTRACTION_FOLDER_NAME)
PLOTS_FOLDER_PATH = os.path.join(os.getcwd(), PLOTS_FOLDER_NAME)

os.makedirs(PLOTS_FOLDER_PATH, exist_ok=True)

def load_data(_url, _store, _verbose):
   os.makedirs(EXTRACTION_FOLDER_NAME, exist_ok=True)

   _req = requests.get(_url)
   z = zipfile.ZipFile(io.BytesIO(_req.content))
   z.extractall(path=EXTRACTION_FOLDER_PATH)
   _file_name = z.namelist()[0]
   _file_path = os.path.join(EXTRACTION_FOLDER_NAME, _file_name)
   df = pd.read_csv(_file_path, low_memory=False)

   if _store:
      if _verbose:
         print(f"Downloaded & Stored the extracted file {_file_name} in the directory {EXTRACTION_FOLDER_NAME}")
   else:
      os.remove(_file_path)

   return df

def cot_hist(cot_report_type = "legacy_fut", store_txt=True, verbose=True):
   try: 
      if cot_report_type== "legacy_fut": 
         url_end = "deacot1986_2016"
         # txt = "FUT86_16.txt"
         if verbose: print("Selected: COT Legacy report. Futures only.")

      elif cot_report_type == "legacy_futopt": 
         url_end = "deahistfo_1995_2016"
         # txt = "Com95_16.txt"
         if verbose: print("Selected: COT Legacy report. Futures and Options.")

      elif cot_report_type == "supplemental_futopt": 
         url_end = "dea_cit_txt_2006_2016"
         # txt = "CIT06_16.txt"
         if verbose: print("Selected: COT Sumpplemental report. Futures and Options.")
   
      elif cot_report_type == "disaggregated_fut": 
         url_end = "fut_disagg_txt_hist_2006_2016"
         # txt = "F_Disagg06_16.txt"
         if verbose: print("Selected: COT Disaggregated report. Futures only.")

      elif cot_report_type == "disaggregated_futopt": 
         url_end = "com_disagg_txt_hist_2006_2016"
         # txt = "C_Disagg06_16.txt"
         if verbose: print("Selected: COT Disaggregated report. Futures and Options.")

      elif cot_report_type == "traders_in_financial_futures_fut": 
         url_end = "fin_fut_txt_2006_2016"
         # txt = "F_TFF_2006_2016.txt" 
         if verbose: print("Selected: COT Traders in Financial Futures report. Futures only.")

      elif cot_report_type == "traders_in_financial_futures_futopt": 
         url_end = "fin_com_txt_2006_2016"
         # txt = "C_TFF_2006_2016.txt" 
         if verbose: print("Selected: COT Traders in Financial Futures report. Futures and Options.")
   except ValueError:
         if verbose: print("""Input needs to be either:
               "legacy_fut", "legacy_futopt", supplemental_futopt",
               "disaggregated_fut", "disaggregated_futopt", 
               "traders_in_financial_futures_fut" or
               "traders_in_financial_futures_futopt" """)

   return load_data("https://cftc.gov/files/dea/history/" + str(url_end) + ".zip", store_txt, verbose)

def cot_year(year = 2020, cot_report_type = "legacy_fut", store_txt=True, verbose=True):    
   if verbose: print("Selected:", cot_report_type)
   try: 
      if cot_report_type== "legacy_fut": 
         rep = "deacot"
         # txt = "annual.txt"
      
      elif cot_report_type == "legacy_futopt": 
         rep = "deahistfo"
         # txt = "annualof.txt"
   
      elif cot_report_type == "supplemental_futopt": 
         rep = "dea_cit_txt_"
         # txt = "annualci.txt"

      elif cot_report_type == "disaggregated_fut": 
         rep = "fut_disagg_txt_"
         # txt = "f_year.txt"

      elif cot_report_type == "disaggregated_futopt": 
         rep = "com_disagg_txt_"
         # txt = "c_year.txt"

      elif cot_report_type == "traders_in_financial_futures_fut": 
         rep = "fut_fin_txt_"
         # txt = "FinFutYY.txt"

      elif cot_report_type == "traders_in_financial_futures_futopt": 
         rep = "com_fin_txt_"
         # txt = "FinComYY.txt"

   except ValueError:    
      print("""Input needs to be either:
               "legacy_fut", "legacy_futopt", supplemental_futopt",
               "disaggregated_fut", "disaggregated_futopt", 
               "traders_in_financial_futures_fut" or
               "traders_in_financial_futures_futopt" """)

   if verbose: print("Loading single year data from:", year)
   return load_data("https://cftc.gov/files/dea/history/" + rep + str(year) + ".zip", store_txt, verbose)

def cot_all(cot_report_type="legacy_fut", store_txt=True, verbose=True, store = True): 
   _cache_file_name = f"{cot_report_type}.csv"
   _cache_file_path = os.path.join(EXTRACTION_FOLDER_PATH, _cache_file_name)

   if os.path.isdir(EXTRACTION_FOLDER_PATH):
      if _cache_file_name in os.listdir(EXTRACTION_FOLDER_PATH):
         if not store: os.remove(_cache_file_path)
         else:
            if verbose: print(f"used cached file {cot_report_type}.csv under the directory: {EXTRACTION_FOLDER_PATH}")
            df = pd.read_csv(_cache_file_path, low_memory=False)
            return df

   df = pd.concat([
      # Get historical data till 2016 (included)  
      cot_hist(cot_report_type, store_txt=store_txt, verbose=verbose),
      pd.concat([cot_year(i, cot_report_type, store_txt=store_txt, verbose=verbose) for i in range(2017, date.today().year+1)])
   ])

   if store:
      df.to_csv(_cache_file_path, index=False)
      if verbose: print(f"data cached in the file {cot_report_type}.csv under the directory: {EXTRACTION_FOLDER_PATH}")

   return df

def cot_all_reports(store_txt=True, verbose=True):   
  l = ["legacy_fut", "legacy_futopt", "supplemental_futopt", "disaggregated_fut", "disaggregated_futopt", "traders_in_financial_futures_fut", "traders_in_financial_futures_futopt"]

  for report in l: 
    if verbose: print(report)
    temp = '{}'.format(report)
    vars()[temp] = cot_all(cot_report_type=report, store_txt=store_txt, verbose=verbose)

  return  vars()['{}'.format("legacy_fut")],vars()['{}'.format("legacy_futopt")],vars()['{}'.format("supplemental_futopt")],\
  vars()['{}'.format("disaggregated_fut")],vars()['{}'.format("disaggregated_futopt")],vars()['{}'.format("traders_in_financial_futures_fut")],\
  vars()['{}'.format("traders_in_financial_futures_futopt")]

def cot_description():
  url = 'https://www.cftc.gov/MarketReports/CommitmentsofTraders/ExplanatoryNotes/index.htm'
  res = requests.get(url)
  html_page = res.content
  soup = BeautifulSoup(html_page, 'html.parser')
  text = soup.find_all(text=True)
  from itertools import groupby
  split_at = "Open Interest"
  text = [list(g) for k, g in groupby(text, lambda x: x != split_at) if k][1]
  split_at = "Supplemental Report"
  text = [list(g) for k, g in groupby(text, lambda x: x != split_at) if k][0]
  print("scraped texts from cftc.gov:")
  print(text)
  x = {'var_info': [
        "open interest (oi)",
        "reportable positions",
        "commercial (c) and non-commercial (nc)",
        "nonreportable positions (nr)",
        "changes in commitments from previous reports",
        "spreading",
        "percent of open interest (oi)",
        "number of traders (traders)",
        "old and other futures",
        "concentration ratios"
  ],        
     'exp_not': [' '.join(text[0:2]),
                 ' '.join(text[3:4]),
                 ' '.join(text[5:10]),
                 ' '.join(text[11:12]),
                 ' '.join(text[13:14]),
                 ' '.join(text[15:16]),
                 ' '.join(text[17:18]), 
                 ' '.join(text[19:20]),
                 ' '.join(text[21:23]), 
                 ' '.join(text[24:25])]}
  df = pd.DataFrame(x, columns = ['var_info', 'exp_not'])
  return df