import requests
import time
import pandas as pd
import numpy as np
from pathlib import Path

SLEEP_TIME = 1

def get_api_response(url:str, params:dict) -> dict:
    response = requests.get(url, params=params)
    print(f'API status code: {response.status_code}')
    return response.json()

def get_games_list(df:pd.DataFrame, export:bool = False, filename:str = 'games_list.txt') -> list:
    
    array_appid = df['appid'].values
    
    if export:    
        file_path = Path(__file__).parent / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as file_gameslist:
            file_gameslist.writelines(f"{app_id}\n" for app_id in array_appid)
        print(f'Exported game list to: {file_path}')
            
    return array_appid

def write_staging_local(df: pd.DataFrame, filename: str) -> None:
    
    file_path = Path(__file__).parent / 'staging' / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(file_path, index=False)
        
    print(f"Sucessfully exported to {file_path}")
    
def transform_steamweb_data(response_data: dict, select_columns: list) -> list:
    
    df = pd.json_normalize(response_data)
        
    gamedata_df = pd.DataFrame()
    for columns in select_columns:
        if columns not in df:
            gamedata_df.loc[:,columns] = np.nan
        else:
            gamedata_df.loc[:,columns] = df[columns]
            
    # gamedata_df['release_date.date'].values[0] = pd.to_datetime(gamedata_df['release_date.date'].values[0], format='%d %b, %Y')
    gamedata_df['release_date.date'].values[0] = pd.to_datetime(gamedata_df['release_date.date'].values[0], format='mixed')
    
    print(gamedata_df['name'].values[0])
    print(gamedata_df['release_date.date'].values[0])
            
    return gamedata_df.values.tolist()[0]

def flow_steamspy_api_to_csv(export_gamelist:bool = False) -> list:
    json_response = get_api_response("https://steamspy.com/api.php", {"request": "all", 'page':'0'}) # Get first page of data (Top 1000 games)
    df = pd.DataFrame(json_response).T
    
    games_list = get_games_list(df, export=export_gamelist, filename='games_list.txt')
    
    write_staging_local(df, filename='steamspy_games.csv')
    
    return games_list

def flow_steamweb_api_to_csv(games_list: list = None , import_gamelist:bool = False, gamelist_path:Path = Path(__name__).parent / 'games_list.txt', language:str = 'english', country:str = 'my') -> None:
    
    table_columns = ['steam_appid',
                'name', 
                'type', 
                'required_age',  
                'is_free',
                'price_overview.currency',
                'price_overview.initial',
                'platforms.windows', 
                'platforms.mac', 
                'platforms.linux', 
                'recommendations.total', 
                'metacritic.score',
                'achievements.total',
                'controller_support', 
                'release_date.date',
                'short_description',
                'detailed_description', 
                'about_the_game']
    
    if import_gamelist:
        with open(gamelist_path, 'r') as file_gameslist:
            games_list = file_gameslist.readlines()
            games_list = [game.strip() for game in games_list]
            
    print(games_list)
    
    game_table = []
    
    for app_id in games_list:
        
        print(f'Getting AppID: {app_id}')
        
        params = {
            'appids': f'{app_id}',  # Steam AppID of game
            'l': f'{language}',     # Language of the game data
            'cc': f'{country}'      # Country Code of the game data, e.g. Malaysia = 'my' (Returns currency in MYR)
        }
        json_response = get_api_response(f"https://store.steampowered.com/api/appdetails", params=params)
    
        if not json_response[f'{app_id}']['success']:
            print(f"Failed to retrieve data for AppID: {app_id}")
            continue
        
        game_table.append(transform_steamweb_data(json_response[f'{app_id}']['data'], select_columns=table_columns))

        time.sleep(SLEEP_TIME)
        
        
    write_staging_local(pd.DataFrame(game_table, columns=table_columns), filename='steamweb_games.csv')
    print('\n')
        
if __name__ == "__main__":
    
    start_time = time.time()
    
    games_list = flow_steamspy_api_to_csv(export_gamelist=True)
    flow_steamweb_api_to_csv(games_list, False)
    
    print(f"--- {time.time() - start_time} seconds ---")
    