import pandas as pd
import requests


def add_teams():
    df = pd.read_csv("data.csv", usecols = ['HC ID'])

    for i in df['HC ID'].to_list():
        dictToSend = {"hcid": str(i)}
        res = requests.post('http://132.147.169.218:5000/register', json=dictToSend)
        if res.status_code == 401:
            # Unauthorized
            pass

def dump_data():
    res = requests.get('http://132.147.169.218:5000/generate-team-file')

def get_scores():
    res = requests.get('http://132.147.169.218:5000/scores')


#add_teams()
#dump_data()
get_scores()