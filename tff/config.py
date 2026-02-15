import pandas as pd

Position_Types = ['Long_All', 'Short_All', 'Spread_All']

MARKET_PARTICIPANTS = ['Dealer', 'Asset_Mgr', 'Lev_Money', 'NonRept', 'Other_Rept']

def get_df_net(df):
    df_net = pd.DataFrame({})

    for participant in MARKET_PARTICIPANTS:
        df_net[f'Net_{participant}'] = df[f'{participant}_Positions_{Position_Types[0]}'] - df[
            f'{participant}_Positions_{Position_Types[1]}']

    return df_net

def get_df_index(df, window = 52):
    df_index = pd.DataFrame({})

    df_net = get_df_net(df)

    for participant in MARKET_PARTICIPANTS:
        df_index[f'Net_{participant}_Min({window})'] = df_net[f'Net_{participant}'].rolling(window=window).min()
        df_index[f'Net_{participant}_Max({window})'] = df_net[f'Net_{participant}'].rolling(window=window).max()
        df_index[f'{participant}_Index({window})'] = 100 * (df_net[f'Net_{participant}'] - df_index[f'Net_{participant}_Min({window})']) / (df_index[f'Net_{participant}_Max({window})'] - df_index[f'Net_{participant}_Min({window})'])
        del df_index[f'Net_{participant}_Min({window})']
        del df_index[f'Net_{participant}_Max({window})']

    df_index.dropna(inplace=True)

    return df_index

def get_df_oi(df):
    df_oi = pd.DataFrame({})

    df_oi['OI'] = df['Open_Interest_All']

    for participant in MARKET_PARTICIPANTS:
        # Long
        df_oi[f'OI_Long_{participant}'] = df_oi['OI'] * df[f'Pct_of_OI_{participant}_{Position_Types[0]}'] / 100
        # Short
        df_oi[f'OI_Short_{participant}'] = df_oi['OI'] * df[f'Pct_of_OI_{participant}_{Position_Types[1]}'] / 100
        # Spread
        if participant != 'NonRept': df_oi[f'OI_Spread_{participant}'] = df_oi['OI'] * df[f'Pct_of_OI_{participant}_{Position_Types[2]}'] / 100

    return df_oi

def get_df_spreading(df):
    df_spreading = pd.DataFrame({})

    for participant in MARKET_PARTICIPANTS:
        if participant != MARKET_PARTICIPANTS[-2]:
            df_spreading[f'Spreading_{participant}'] = df[f'{participant}_Positions_{Position_Types[2]}']

    return df_spreading