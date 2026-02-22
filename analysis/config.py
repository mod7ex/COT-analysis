import pandas as pd
import json
import random
from utils import print_json

# --------------------------------------------------------------------------------------------------------------------------------------------

def get_market_participants(market_df):

    participants = {}

    for col in market_df.columns:
        if "positions" not in col or "all" not in col: continue

        if "long" in col:
            side = "long"
        elif "short" in col:
            side = "short"
        elif "spread" in col:
            side = "spread"
        else:
            continue

        participant = col.split("_positions")[0]

        if participant not in participants: participants[participant] = {
            "oi_all": "open_interest_all"
        }

        participants[participant][side] = col

    for col in market_df.columns:
        if "_oi_" not in col or 'all' not in col: continue

        if "long" in col:
            side = "long_oi"
        elif "short" in col:
            side = "short_oi"
        elif "spread" in col:
            side = "spread_oi"
        else:
            continue

        for participant in participants.keys():
            if participant in col:
                participants[participant][side] = col

    for col in market_df.columns:
        if "change_in" not in col or 'all' not in col: continue

        if "long" in col:
            side = "long_change"
        elif "short" in col:
            side = "short_change"
        elif "spread" in col:
            side = "spread_change"
        else:
            continue

        for participant in participants.keys():
            if participant in col:
                participants[participant][side] = col

    return participants

# --------------------------------------------------------------------------------------------------------------------------------------------

net_participant_col = lambda participant: f"Net_{participant}"
spread_participant_col = lambda participant: f"Spreading_{participant}"
oi_participant_col = lambda participant, side: f"OI_{side}_{participant}"

# --------------------------------------------------------------------------------------------------------------------------------------------

def get_market_net(market_df, participants: dict):

    df_net = pd.DataFrame(index=market_df.index)

    # build net columns
    for participant, sides in participants.items():
        if "long" in sides and "short" in sides:
            df_net[net_participant_col(participant)] = market_df[sides["long"]] - market_df[sides["short"]]

    return df_net

# --------------------------------------------------------------------------------------------------------------------------------------------

def get_market_cotIndex(market_df, participants: dict,window = 52):
    df_index = pd.DataFrame({})

    df_net = get_market_net(market_df, participants)

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

def get_market_oi(market_df, participants: dict):
    df_oi = pd.DataFrame({})

    _random_participant = random.choice(list(participants.keys()))

    df_oi['OI'] = market_df[participants[_random_participant]['oi_all']]

    for participant, side in participants.items():
        df_oi[oi_participant_col(participant, 'long')] = df_oi['OI'] * market_df[side['long_oi']] / 100
        df_oi[oi_participant_col(participant, 'short')] = df_oi['OI'] * market_df[side['short_oi']] / 100
        if 'spread' in side:
            df_oi[oi_participant_col(participant, 'spread')] = df_oi['OI'] * market_df[side['spread_oi']] / 100

    return df_oi

# --------------------------------------------------------------------------------------------------------------------------------------------

def get_market_spreading(market_df, participants: dict):
    df_spreading = pd.DataFrame({})

    for participant, side in participants.items():
        if 'spread' in side:
            df_spreading[spread_participant_col(participant)] = market_df[side['spread']]

    return df_spreading