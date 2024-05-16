import json
import requests
import time
import pandas as pd
import numpy as np
from pathlib import Path

TIME_SLEEP = 1.5 # Period of time to sleep im between requests (Steam API limits up to 200 requests per 5 minits; average 1.5 sec per request)

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

def get_games_list() -> list:
    '''Get list of Steam Games's AppID from text file'''
    
    id_list = []
    with open('txt/games_list.txt') as gameslist:
        games = gameslist.readlines()
        for appid in games:
            appid = appid.strip()
            id_list.append(appid)
    
    return id_list

def get_api_response(app_id:str, language:str = 'english', country:str = 'my') -> dict:
    '''Retrieves API response from url'''
    
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&l={language}&cc={country}"
    
    while True:
        response = requests.get(url)
        print(response.status_code)
        if response.status_code == 200:
            break
        time.sleep(10)

    return json.loads(response.text)

def clean_data(response: dict, app_id: str) -> list:
    '''Normalize API response and filters out unwanted keys'''
    
    try:
        df = pd.json_normalize(response[f'{app_id}']['data'])
        
        gamedata_df = pd.DataFrame()
        for columns in select_columns:
            if columns not in df:
                gamedata_df.loc[:,columns] = np.nan
            else:
                gamedata_df.loc[:,columns] = df[columns]
        
        return gamedata_df.values.tolist()
    
    except:
        print(f"Failed to read data for AppID: {app_id}")
        return None
    
def write_to_local(gameslist: list) ->None:
    '''Write DataFrame into csv locally'''
    
    print("Writing gameinfo into CSV file...")
    
    csv_path = Path('./csv/steamapi_games_list.csv')
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(gameslist, columns=select_columns)
    
    try:
        df.to_csv(csv_path, index=False)
        print("Sucessfully written into CSV file")
    except Exception as e:
        print(f"Failed writing into CSV file. Error: {e}")
    
def flow_ingest_steamapi(language:str = 'english', country:str = 'my') -> None:
    '''Main flow for ingesting data from Steam API based on game list'''

    games_appid = get_games_list()
    list_games_tables = []
    list_fail = []
    
    for app_id in games_appid:
        response = get_api_response(app_id, language, country)
        list_gameinfo = clean_data(response, app_id)
        
        # skip over current loop if failed to retrieve data
        if not list_gameinfo:
            list_fail.append(app_id)
            continue
        
        for info in list_gameinfo:
            list_games_tables.append(info)
            
        print(f"Sucessfully written data for AppID: {app_id}")
        time.sleep(TIME_SLEEP)
        
    print("Failed to retrieve data for AppIDs: ")
    for failures in list_fail:
        print(failures)
    
    write_to_local(list_games_tables)
                
if __name__ == '__main__':
    flow_ingest_steamapi()
    