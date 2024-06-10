import json
import requests
import time
import pandas as pd
from pathlib import Path

def get_api_response(url:str) -> dict:
    '''
    Retrieves API response from url into JSON
    
        url (str): HTML address for the API
        
    '''
    response = requests.get(url)
    
    if not response.status_code == '220':
        print(response.status_code)
        # add code to handle unsucessful request later...
        
    return json.loads(response.text)

def get_games_list(data: dict) -> list:
    '''Returns a list of AppIDs from response data'''
    df = pd.DataFrame(data).T
    return df['appid'].values.tolist()

def create_game_list(list: list, path:str = './games_list.txt') -> None:
    '''Writes a list of AppIDs into a txt file'''
    file_path = Path(path)
    with open(file_path, 'w') as file_gameslist:
        file_gameslist.writelines(f"{app_id}\n" for app_id in list)
        
def clean_data_to_list(data: dict) -> list:
    df = pd.DataFrame(data).reset_index(drop=True)
    df.drop(['tags'], axis=1, inplace=True)
    df.drop(df.index[1:], inplace=True)
    
    return df.values.tolist()

def write_to_local(gamedata:list, path:str = './csv/steamspy_game_list.csv') -> None:
    '''Write DataFrame into csv locally'''
    table_columns = ['appid',
                    'name',
                    'developer',
                    'publisher',
                    'score_rank',
                    'positive',
                    'negative',
                    'userscore',
                    'owners',
                    'average_forever',
                    'average_2weeks',
                    'median_forever',
                    'median_2weeks',
                    'price',
                    'initialprice',
                    'discount',
                    'ccu',
                    'languages',
                    'genre']
    
    print("Writing gameinfo into CSV file...")

    df = pd.DataFrame(gamedata, columns=table_columns)
    df.index += 1
    csv_path = Path(path)
    df.to_csv(path_or_buf=csv_path, index_label='ownership_ranking')
    
def flow_main_api_to_csv() -> None:
    '''Main flow for retrieving data from SteamSpy API'''

    all_games_data = []
    data = get_api_response('https://steamspy.com/api.php?request=all&page=0')
    games_list = get_games_list(data)
    create_game_list(games_list)
    
    for appid in games_list:
        game_data = get_api_response(url=f"https://steamspy.com/api.php?request=appdetails&appid={appid}")
        
        for info in clean_data_to_list(game_data):
            all_games_data.append(info)  
        print(f"Sucessfully retrieved data for AppID: {appid}")
        time.sleep(0.2)
        
    games_list = None
    write_to_local(all_games_data)
    all_games_data = None
    
if __name__ == '__main__':
    flow_main_api_to_csv()