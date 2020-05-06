from prettytable import PrettyTable
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import pandas as pd
import sys

COLUMN_NAMES_ = {"g": "Games",
                 "gs": "Games Started",
                 "mp_per_g": "Minutes per Game",
                 "fg_per_g": "Field Goals Per Game",
                 "fga_per_g": "Field Goal Attempts",
                 "fg_pct": "FieldGoal %",
                 "fg3_per_g": "3 Pointers per game",
                 "fg3a_per_g": "3 pointer Attempts",
                 "fg3_pct": "3 Pointer %",
                 "fg2_per_g": "2 Pointers per game",
                 "fg2a_per_g": "2 pointer Attempts",
                 "fg2_pct": "2 Pointer %",
                 "efg_pct": "Effective Field Goal %",
                 "ft_per_g": "Freethrows per Game",
                 "fta_per_g": "Freethrow Attempts per Game",
                 "ft_pct": "Freethrow %",
                 "orb_per_g": "Offensive Rebounds per Game",
                 "drb_per_g": "Defensive Rebounds per Game",
                 "trb_per_g": "Total Rebounds Per Game",
                 "ast_per_g": "Assists per Game",
                 "stl_per_g": "Steals per Game",
                 "blk_per_g": "Blocks per Game",
                 "tov_per_g": "Turnovers per Game",
                 "pf_per_g": "Personal Fouls per Game",
                 "pts_per_g": "Points per Game"}

COLUMN_NAMES = {"g": "G",
                "gs": "GS",
                "mp_per_g": "MP",
                "fg_per_g": "FG",
                "fga_per_g": "FGA",
                "fg_pct": "FG%",
                "fg3_per_g": "3P",
                "fg3a_per_g": "3PA",
                "fg3_pct": "3%",
                "fg2_per_g": "2P",
                "fg2a_per_g": "2PA",
                "fg2_pct": "2P%",
                "efg_pct": "eFG%",
                "ft_per_g": "FT",
                "fta_per_g": "FTA",
                "ft_pct": "FT%",
                "orb_per_g": "ORB",
                "drb_per_g": "DRB",
                "trb_per_g": "TRB",
                "ast_per_g": "AST",
                "stl_per_g": "STL",
                "blk_per_g": "BLK",
                "tov_per_g": "TOV",
                "pf_per_g": "PF",
                "pts_per_g": "PTS"}

BBREFERENCE_URL = "https://www.basketball-reference.com/players"
DROPPED_COLUMNS = ['age', 'team_id', 'lg_id', 'pos']

# use the player's first and last name to
# create the URL for their basketball reference page
def get_url(player_name):
    # split name
    player_name = player_name.lower()
    first, last = player_name.split(" ")

    # trim name
    first = first[:2]
    last = last[:5]
    first_initial = last[0]

    # create the player's url
    url = BBREFERENCE_URL
    url += "/" + first_initial + "/" + last + first + "01" + ".html"

    return url


# get career stats from specified url
def get_data(url):
    try:
        html = urlopen(url)
    except HTTPError as err:
        if err.code == 404:
            print("player not found  -  " + url)
            exit()

    # use beautiful soup to get career stats from basketball reference
    soup = BeautifulSoup(html, 'lxml')
    stats_table = (soup.find('div', id="all_per_game"))
    career_stats = stats_table.find('tfoot')
    career_stats = career_stats.find('tr')

    # put stats into dict then convert to data frame
    stats_dict = {}
    for column in career_stats.find_all('td'):
        stats_dict[column.attrs['data-stat']] = column.text

    return pd.DataFrame(stats_dict, index=[0])


# combine the two career stats into one data frame
def combine_stats(df1, df2):
    return pd.concat([df1, df2], sort=False)


# remove unnecessary columns and rename columns for readibility
def clean_stats(df):
    df = df.drop(DROPPED_COLUMNS, axis=1)
    return df.rename(columns=COLUMN_NAMES)


def main():
    # using command line arguments fetch stats for both players
    results = clean_stats(combine_stats(
        get_data(get_url(sys.argv[1] + " " + sys.argv[2])),
        get_data(get_url(sys.argv[3] + " " + sys.argv[4])),
    ))

    # create prettyTable for displaying stats
    final = PrettyTable()

    # specify column names on pretty table
    final.field_names = [(sys.argv[1] + " " + sys.argv[2]),
                         "STATS", (sys.argv[3] + " " + sys.argv[4])]

    # add the stats from the data frame into the pretty table
    for column in results:
        final.add_row([results.iloc[0][column],
                       column, results.iloc[1][column]])

    # display stats table
    print(final)


if __name__ == "__main__":
    main()