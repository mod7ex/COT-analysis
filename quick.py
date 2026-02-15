import pandas as pd
from utils.cot import cot_all
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Default Vars -----------------------------------------------------------------------------------------------------------------
_ASSET_CODE = '088691'
_STARTING_DATE = '2020'
_PLOT_FILE_NAME = 'quick_analysis'
_WINDOW = 52 # Rolling window for the last N weeks
# -----------------------------------------------------------------------------------------------------------------

df = cot_all()

# Inputs -----------------------------------------------------------------------------------------------------------------
asset_code_input = input(f"Enter the asset code you want to analyse (default: {_ASSET_CODE}) [press ENTER to ignore]: ")
ASSET_CODE = asset_code_input if asset_code_input else _ASSET_CODE

starting_date_input = input(f"Enter the starting date (default: {_STARTING_DATE}) [press ENTER to ignore]: ")
STARTING_DATE = starting_date_input if starting_date_input else _STARTING_DATE

window_input = input(f"Enter the window <int> (default: {_WINDOW} weeks) [press ENTER to ignore]: ")
WINDOW = int(window_input) if window_input else _WINDOW

plot_file_name_input = input(f"Enter plot file name (default: {_PLOT_FILE_NAME}) [press ENTER to ignore]: ")
PLOT_FILE_NAME = plot_file_name_input if plot_file_name_input else _PLOT_FILE_NAME

df = df[df['CFTC Contract Market Code'] == ASSET_CODE]

ASSET_NAME = df['Market and Exchange Names'].iloc[0].split(' - ')[0].strip()

print(f"[->] Filtered data for asset code {ASSET_CODE} ({ASSET_NAME}).")
# -----------------------------------------------------------------------------------------------------------------

df = df.rename(columns={'As of Date in Form YYYY-MM-DD': 'Date'})

df['Date'] = pd.to_datetime(df['Date'])

df.set_index('Date', inplace=True)

df.sort_index(inplace=True)

# Net positions
df['Commercial_Net_Position'] = df['Commercial Positions-Long (All)'] - df['Commercial Positions-Short (All)']
df['Large_Speculators_Net_Position'] = df['Noncommercial Positions-Long (All)'] - df['Noncommercial Positions-Short (All)']
df['Small_Traders_Net_Position'] = df['Nonreportable Positions-Long (All)'] - df['Nonreportable Positions-Short (All)']
print("[->] Calculated net positions for Commercials, Large Speculators, and Small Traders.")

# Calculate COT Index for Commercials

df['Max_Net_Position_Last_N'] = df['Commercial_Net_Position'].rolling(window=WINDOW).max()
df['Min_Net_Position_Last_N'] = df['Commercial_Net_Position'].rolling(window=WINDOW).min()

df.dropna(inplace=True)

df['COT_Index'] = 100 * (df['Commercial_Net_Position'] - df['Min_Net_Position_Last_N'])/(df['Max_Net_Position_Last_N'] - df['Min_Net_Position_Last_N'])
print("[->] Calculated COT Index for Commercials.")

# ----------------------------------------------------------------------------------------------------------------------------

df = df[['Commercial_Net_Position', 'Large_Speculators_Net_Position', 'Small_Traders_Net_Position', 'COT_Index', 'Open Interest (All)']]
df = df.rename(columns={'Open Interest (All)': 'OI'})

# ----------------------------------------------------------------------------------------------------------------------------
df = df[df.index > STARTING_DATE]  # Filter by starting date if needed
# ----------------------------------------------------------------------------------------------------------------------------
print("[->] Preparing data for plotting...")

# Create subplots: 1 column, 3 rows, shared X-axis
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing= 0.1, subplot_titles=(f"COT index ({WINDOW} weeks)", 'Net positions', 'OI'))

# Add each series to its own subplot
fig.add_trace(go.Scatter(x=df.index, y=df['COT_Index'], name='COT Index'), row=1, col=1)
for col in ['Commercial_Net_Position', 'Large_Speculators_Net_Position', 'Small_Traders_Net_Position']:
    fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col.replace('_Net_Position', '').replace('_', ' ').title(), line=dict(width=2)), row=2, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['OI'], name='OI'), row=3, col=1)

fig.add_shape(
    type='rect',
    xref='paper',  # spans the full width of the plot
    yref='y1',  # y-axis of subplot in row 1
    x0=0,
    x1=1,
    y0=80,       # Adjust based on your y-axis range
    y1=100,
    fillcolor='green',
    opacity=0.2,
    line_width=0,
    layer='below'
)

fig.add_shape(
    type='rect',
    xref='paper',  # spans the full width of the plot
    yref='y1',  # y-axis of subplot in row 1
    x0=0,
    x1=1,
    y0=0,              # Adjust based on your y-axis range
    y1=20,
    fillcolor='red',
    opacity=0.2,
    line_width=0,
    layer='below'
)

# Update layout
fig.update_layout(
    height=900,
    width=1450,
    title_text=f"COT Analysis for {ASSET_NAME}",
    template='plotly_dark',
    hovermode='x unified',  # or 'x unified' or 'closest',
)

fig.update_xaxes(title_text='Date', row=3, col=1)  # Only show x-axis label on bottom chart
fig.update_yaxes(title_text='CONTRACT')

# Save as responsive HTML
fig.write_html(f"plots/{PLOT_FILE_NAME}.html", auto_open=False, full_html=True, include_plotlyjs='cdn', config={'responsive': True})

print("[->] Plot saved as 'plots/quick_analysis.html'.")
print(f"[->] use Live Server to view the plot in your browser. http://localhost:5500/plots/{PLOT_FILE_NAME}.html")