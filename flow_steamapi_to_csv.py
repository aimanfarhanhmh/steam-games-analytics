import json
import requests
import time
import pandas as pd
import numpy as np
from pathlib import Path

# Columns to be filtered out from api response
select_columns = ['steam_appid',
                  'name', 
                  'type', 
                  'required_age',  
                  'is_free',
                  'price_overview.currency',
                  'price_overview.initial',
                  'detailed_description', 
                  'about_the_game', 
                  'short_description', 
                  'platforms.windows', 
                  'platforms.mac', 
                  'platforms.linux', 
                  'recommendations.total', 
                  'metacritic.score',
                  'achievements.total',
                  'controller_support', 
                  'release_date.date']

def get_api_response(app_id:str):
    
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&l=english"

    response = requests.get(url)
    print("Response Code: " + str(response.status_code))
    if (response.status_code == '429'):
        time.sleep(10)
        return get_api_response(app_id)

    return json.loads(response.text)[f"{app_id}"]['data']

def load_dataframe(data) -> pd.DataFrame:
    df = pd.json_normalize(data)
    gamedata_df = pd.DataFrame()
    
    for columns in select_columns:
        if columns not in df:
            gamedata_df.loc[:,columns] = np.nan
        else:
            gamedata_df.loc[:,columns] = df[columns]
    
    return gamedata_df

def write_to_csv(df: pd.DataFrame, app_id: str) -> str:
    if Path('./gamedata.csv').is_file():
        df.to_csv('gamedata.csv', mode='a', index=False, header=False)
    else:
        df.to_csv('gamedata.csv', mode='a', index=False, header=True)
        
    return f'Writing game data for AppID {app_id} sucessful'
    
if __name__ == '__main__':

    games_appid = []

    with open('txt/games_list.txt') as gameslist:
        games = gameslist.readlines()
        for appid in games:
            appid = appid.strip()
            games_appid.append(appid)
            
    for i in games_appid:
        try:
            data = get_api_response(i)
            df = load_dataframe(data)
            print(write_to_csv(df, i))
            time.sleep(1.5)
        except Exception as e:
            print(f'Failed to retrieve game data for AppID {i} \nError Code: {e}')
            continue