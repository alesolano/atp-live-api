import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def get_atp_live_dataframe():

    req = urllib.request.Request('http://live-tennis.eu/en/atp-live-ranking')
    response = urllib.request.urlopen(req)

    html = response.read()

    soup = BeautifulSoup(html, "html.parser")

    # Data in websites are usually printed as tables.
    # The first thing we should do is find the data table we're interested in.
    # t6868 is the name of the data table. Yes, it's not a very descriptive name.
    table = soup.find("table", attrs={"id": "t868"})

    # Tables are structed in rows.
    # A row may have a name, or 'class', which identifies it.
    # Rows are abbreviated as <tr> (tag row)
    players = []
    for row in table.find_all("tr"):
        try:
            country = row['class'][0]
            if country.isupper() and len(country) == 3: # looking for 'GBR', 'SPA', 'SWI'...
                players.append(row)
        except:
            pass

    cols = ['ranking', 'career_high', '_1', 'name', 'age', 'country', 'points', 
    'rank_change', 'points_change', 'curr_tournament', 'prev_tournament', '_2', 'next_points', 'if_win_points']

    #murray = players[0]
    #murray_dir = {col: data.get_text().replace(u'\xa0', u'') for col, data in zip(cols, murray.find_all("td"))}
    #murray_series = pd.Series(murray_dir)
    #murray_series = murray_series.drop(['_1', '2'])

    df = pd.DataFrame(columns=cols)
    for player in players:
        data = [col_data.get_text().replace(u'\xa0', u'') for col_data in player.find_all("td")]
        df = pd.concat([df, pd.DataFrame([data], columns=cols)])

    numeric_cols = ['ranking', 'age', 'points', 'rank_change', 'points_change', 'next_points', 'if_win_points']
    for col in numeric_cols:
        df[col] = df[col].apply(pd.to_numeric, errors='coerce')

    # Este es un caso especialito
    df.career_high = df.career_high.apply(pd.to_numeric, errors='ignore')

    df = df.drop(['_1', '_2'], 1) # 1 is for columns. (0 is for rows)

    #df = df.set_index('ranking')
    index = [i for i in range(1,801)]
    df.index = index

    for player in index:
        df = df.set_value(player, 'country', df['country'].loc[player][:3])

    return df

def get_future_stars(atp_df, max_age=20, max_ranking=100):
    return atp_df[np.logical_and(
        atp_df.age < max_age, 
        atp_df.ranking < max_ranking)]

def get_players_participating_in(atp_df, tournament):
    return atp_df[np.logical_or(
        atp_df.prev_tournament.str.contains(tournament), 
        atp_df.curr_tournament.str.contains(tournament))]
