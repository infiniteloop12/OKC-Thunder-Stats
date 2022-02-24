import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template, request

okc = {
    1628983: "Shai Gilgeous-Alexander",
    1630581: "Josh Giddey",
    1629652: "Luguentz Dort",
    1629647: "Darius Bazley",
    1630177: "Theo Maledon",
    202324: "Derrick Favors",
    1629660: "Ty Jerome",
    1630197: "Aleksej Pokusevski",
    1630598: "Aaron Wiggins",
    1629676: "Isaiah Roby",
    1630544: "Tre Mann",
    1630249: "Vit Krejci",
    203488: "Mike Muscala",
    1629026: "Kenrich Williams",
    1630526: "Jeremiah Robinson-Earl"
}

for player_id in okc:
    url_base = 'https://stats.nba.com/stats/shotchartdetail'

    headers = {
        'Host': 'stats.nba.com',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'Referer': 'https://stats.nba.com/',
        "x-nba-stats-origin": "stats",
        "x-nba-stats-token": "true",
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    parameters = {
        'ContextMeasure': 'FGA',
        'LastNGames': 0,
        'LeagueID': '00',
        'Month': 0,
        'OpponentTeamID': 0,
        'Period': 0,
        'PlayerID': player_id,
        'SeasonType': 'Regular Season',
        'TeamID': 0,
        'VsDivision': '',
        'VsConference': '',
        'SeasonSegment': '',
        'Season': '2021-22',
        'RookieYear': '',
        'PlayerPosition': '',
        'Outcome': '',
        'Location': '',
        'GameSegment': '',
        'GameId': '',
        'DateTo': '',
        'DateFrom': ''
    }

    response = requests.get(url_base, params=parameters, headers=headers)
    content = json.loads(response.content)
    # print(content)

    # transform contents into dataframe
    results = content['resultSets'][0]
    result_headers = results['headers']
    rows = results['rowSet']
    df = pd.DataFrame(rows)
    df.columns = result_headers
    df_made = df[df['SHOT_MADE_FLAG'] == 1]
    df_missed = df[df['SHOT_MADE_FLAG'] == 0]
    # write to csv file
    df.to_csv('sga_shotchart.csv', index=False)

    PLAYER_NAME = df['PLAYER_NAME'][0]
    YEAR = df['GAME_DATE'][0][:4]
    MAKES = int(len(df_made))
    MISSES = int(len(df_missed))
    PERCENTAGE = round(MAKES / (MAKES + MISSES) * 100, 2)
    # set nba_court.jpg to img for graph background
    img = plt.imread('nba_court.jpg')

    # plot LOC_X LOC_Y SHOT_MADE_FLAG
    # handles=
    labels = [f'Makes: {MAKES}', f'Misses: {MISSES}']

    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    plt.title(f"Player: {PLAYER_NAME} Season: {YEAR}-{int(YEAR) + 1}")
    plt.text(165, -325, f'FG%: {PERCENTAGE}%')
    plt.xlim(-250, 250)
    plt.ylim(40, -400)
    ax.imshow(img, extent=[-250, 250, 40, -400])
    scatter = ax.scatter(x=-df_made['LOC_X'], y=-df_made['LOC_Y'], c='green', edgecolors='none', alpha=0.6, marker='o',
                         s=100)
    scatter = ax.scatter(x=-df_missed['LOC_X'], y=-df_missed['LOC_Y'], c='red', alpha=0.4, marker='x')
    plt.xticks([])
    plt.yticks([])
    ax.legend(labels=labels, loc='upper right', title='Shots')
    plt.savefig(f'static/{PLAYER_NAME}.png')
    print(PLAYER_NAME)
    # plt.show()

app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def main_page():
    player = okc[1628983]
    if request.method == "POST":
        player = request.form['player']
        return render_template("index.html", team=okc, player=player)
    return render_template("index.html", team=okc, player=player)


if __name__ == "__main__":
    app.run(debug=True)
