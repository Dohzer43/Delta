#!/usr/bin/env python3
"""
last5_boxscore_full.py

Fetches and prepares the last five games worth of full batting and pitching data for each MLB player.
Outputs six CSVs:
  - raw_last5_batting.csv  : batting lines for each player's last 5 games
  - agg_last5_batting.csv  : aggregated batting totals and rates
  - wide_last5_batting.csv : wide-format batting features per game (g1–g5)
  - raw_last5_pitching.csv : pitching lines for each pitcher's last 5 games
  - agg_last5_pitching.csv : aggregated pitching totals and rates
  - wide_last5_pitching.csv: wide-format pitching features per game (g1–g5)

Usage:
  pip install statsapi pandas
  python last5_boxscore_full.py
"""

import statsapi
import pandas as pd
from datetime import datetime, timedelta

# 1) Define date window (look back 10 days to capture at least 5 game days)
today      = datetime.today().date()
start_date = today - timedelta(days=10)
end_date   = today

# 2) Fetch schedule and filter to completed games
games = statsapi.schedule(
    start_date=start_date.strftime("%Y-%m-%d"),
    end_date  =end_date.strftime("%Y-%m-%d")
)
games = [g for g in games if g['status'] == 'Final']

# Prepare containers
bat_records = []
pitch_records = []

# 3) Extract batting and pitching lines per game per game
for game in games:
    gd  = game['game_date']
    box = statsapi.boxscore_data(game['game_id'])

    # BATTERS
    for side_key, side in (('awayBatters', 'away'), ('homeBatters', 'home')):
        for e in box.get(side_key, [])[1:]:
            try:
                bat_records.append({
                    'player_id':   int(e.get('personId', 0)),
                    'player_name': e.get('name', ''),
                    'team_side':   side,
                    'game_date':   gd,
                    'AB':          int(e.get('ab',    0)),
                    'R':           int(e.get('r',     0)),
                    'H':           int(e.get('h',     0)),
                    '2B':          int(e.get('doubles',0)),
                    '3B':          int(e.get('triples',0)),
                    'HR':          int(e.get('hr',    0)),
                    'RBI':         int(e.get('rbi',  0)),
                    'SB':          int(e.get('sb',    0)),
                    'BB':          int(e.get('bb',    0)),
                    'K':           int(e.get('k',     0)),
                    'LOB':         int(e.get('lob',   0)),
                    'AVG':         float(e.get('avg') or 0),
                    'OBP':         float(e.get('obp') or 0),
                    'SLG':         float(e.get('slg') or 0),
                    'OPS':         float(e.get('ops') or 0)
                })
            except ValueError:
                continue

    # PITCHERS
    for side_key, side in (('awayPitchers', 'away'), ('homePitchers', 'home')):
        for p in box.get(side_key, [])[1:]:
            try:
                pitch_records.append({
                    'player_id':    int(p.get('personId', 0)),
                    'player_name':  p.get('name', ''),
                    'team_side':    side,
                    'game_date':    gd,
                    'IP_outs':      int(p.get('out',   0)),  # outs recorded
                    'H_allowed':    int(p.get('h',     0)),
                    'R_allowed':    int(p.get('r',     0)),
                    'ER_allowed':   int(p.get('er',    0)),
                    'BB_allowed':   int(p.get('bb',    0)),
                    'SO':           int(p.get('so',    0)),
                    'HR_allowed':   int(p.get('hr',    0)),
                    'ERA':          float(p.get('era') or 0),
                    'BF':           int(p.get('bf',    0)),
                    'PC':           int(p.get('pc',    0))   # pitches thrown
                })
            except ValueError:
                continue

# --- BATTING PROCESSING ---
bat_df = pd.DataFrame(bat_records)
bat_df['game_date'] = pd.to_datetime(bat_df['game_date'])
bat_df = bat_df.sort_values(['player_id','game_date'], ascending=[True, False])
raw_bat5 = bat_df.groupby('player_id', as_index=False).head(5)
raw_bat5.to_csv('raw_last5_batting.csv', index=False)

agg_bat = (
    raw_bat5
    .groupby(['player_id','player_name'], as_index=False)
    .agg(
        G   =('game_date','nunique'),
        AB  =('AB','sum'),
        R   =('R','sum'),
        H   =('H','sum'),
        X2B =('2B','sum'),
        X3B =('3B','sum'),
        HR  =('HR','sum'),
        RBI =('RBI','sum'),
        SB  =('SB','sum'),
        BB  =('BB','sum'),
        K   =('K','sum'),
        LOB =('LOB','sum'),
        AVG =('AVG','mean'),
        OBP =('OBP','mean'),
        SLG =('SLG','mean'),
        OPS =('OPS','mean')
    )
)
agg_bat = agg_bat.sort_values('AB', ascending=False)
agg_bat.to_csv('agg_last5_batting.csv', index=False)

# wide batting
fields_bat = ['AB','R','H','2B','3B','HR','RBI','SB','BB','K','LOB','AVG','OBP','SLG','OPS']
bat5 = raw_bat5.copy()
bat5['rank'] = bat5.groupby('player_id').cumcount()+1
wide_bat = bat5.pivot(index=['player_id','player_name'], columns='rank', values=fields_bat)
wide_bat.columns = [f"{stat}_g{rank}" for stat,rank in wide_bat.columns]
wide_bat = wide_bat.reset_index()
wide_bat.to_csv('wide_last5_batting.csv', index=False)

# --- PITCHING PROCESSING ---
pitch_df = pd.DataFrame(pitch_records)
pitch_df['game_date'] = pd.to_datetime(pitch_df['game_date'])
pitch_df = pitch_df.sort_values(['player_id','game_date'], ascending=[True, False])
raw_pitch5 = pitch_df.groupby('player_id', as_index=False).head(5)
raw_pitch5.to_csv('raw_last5_pitching.csv', index=False)

agg_pitch = (
    raw_pitch5
    .groupby(['player_id','player_name'], as_index=False)
    .agg(
        G     =('game_date','nunique'),
        Outs  =('IP_outs','sum'),
        H     =('H_allowed','sum'),
        R     =('R_allowed','sum'),
        ER    =('ER_allowed','sum'),
        BB    =('BB_allowed','sum'),
        SO    =('SO','sum'),
        HR    =('HR_allowed','sum'),
        ERA   =('ERA','mean'),
        BF    =('BF','sum'),
        PC    =('PC','sum')
    )
)
agg_pitch = agg_pitch.sort_values('Outs', ascending=False)
agg_pitch.to_csv('agg_last5_pitching.csv', index=False)

# wide pitching
fields_pitch = ['IP_outs','H_allowed','R_allowed','ER_allowed','BB_allowed','SO','HR_allowed','ERA','BF','PC']
pitch5 = raw_pitch5.copy()
pitch5['rank'] = pitch5.groupby('player_id').cumcount()+1
wide_pitch = pitch5.pivot(index=['player_id','player_name'], columns='rank', values=fields_pitch)
wide_pitch.columns = [f"{stat}_g{rank}" for stat,rank in wide_pitch.columns]
wide_pitch = wide_pitch.reset_index()
wide_pitch.to_csv('wide_last5_pitching.csv', index=False)

print("Generated batting and pitching CSVs for last 5 games per player.")
