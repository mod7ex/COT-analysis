import pandas as pd

# --------------------------------------------------------------------------------------------------------------------------------------------

def get_market_participants(df_market):
    participants = {}

    for col in df_market.columns:
        if "positions" not in col or "all" not in col: continue

        # detect long/short
        if "long" in col: side = "long"
        elif "short" in col: side = "short"
        elif "spread" in col: side = "spread"
        else: continue

        # extract participant name (everything before "positions")
        participant = col.split("_positions")[0]

        if participant not in participants: participants[participant] = {}

        participants[participant][side] = col

    for col in df_market.columns:
        if "_oi_" not in col or 'all' not in col: continue

        # detect long/short
        if "long" in col: side = "long_oi"
        elif "short" in col: side = "short_oi"
        elif "spread" in col: side = "spread_oi"
        else: continue

        for participant in participants.keys():
            if participant in col:
                participants[participant][side] = col

    return participants

# --------------------------------------------------------------------------------------------------------------------------------------------

net_participant_col = lambda participant: f"Net_{participant}"
spread_participant_col = lambda participant: f"Spreading_{participant}"
oi_participant_col = lambda participant, side: f"OI_{side}_{participant}"

# --------------------------------------------------------------------------------------------------------------------------------------------

def get_market_net(df_market):

    df_net = pd.DataFrame(index=df_market.index)

    participants = get_market_participants(df_market)

    # build net columns
    for participant, sides in participants.items():
        if "long" in sides and "short" in sides:
            df_net[net_participant_col(participant)] = df_market[sides["long"]] - df_market[sides["short"]]

    return df_net

# --------------------------------------------------------------------------------------------------------------------------------------------

def get_market_cotIndex(market_df, window = 52):
    df_index = pd.DataFrame({})

    df_net = get_market_net(market_df)

    participants = get_market_participants(market_df)

    for participant in participants:
        _npc = net_participant_col(participant)
        _npc_min = f'{_npc}_Min({window})'
        _npc_max = f'{_npc}_Max({window})'

        df_index[_npc_min] = df_net[_npc].rolling(window=window).min()
        df_index[_npc_max] = df_net[_npc].rolling(window=window).max()
        df_index[f'{participant}_Index({window})'] = 100 * (df_net[_npc] - df_index[_npc_min]) / (df_index[_npc_max] - df_index[_npc_min])
        del df_index[_npc_min]
        del df_index[_npc_max]

    df_index.dropna(inplace=True)

    return df_index

# --------------------------------------------------------------------------------------------------------------------------------------------

def get_market_oi(df):
    df_oi = pd.DataFrame({})

    df_oi['oi'] = df['open_interest_all']

    participants = get_market_participants(df)

    for participant, side in participants.items():
        df_oi[oi_participant_col(participant, 'long')] = df_oi['oi'] * df[side['long_oi']] / 100
        df_oi[oi_participant_col(participant, 'short')] = df_oi['oi'] * df[side['short_oi']] / 100
        if 'spread' in side:
            df_oi[oi_participant_col(participant, 'spread')] = df_oi['oi'] * df[side['spread_oi']] / 100

    return df_oi

# --------------------------------------------------------------------------------------------------------------------------------------------

def get_market_spreading(df):
    df_spreading = pd.DataFrame({})

    participants = get_market_participants(df)

    for participant, side in participants.items():
        if 'spread' in side:
            df_spreading[spread_participant_col(participant)] = df[side['spread']]

    return df_spreading