import json
import requests
import time
import pandas as pd
from pathlib import Path

API_URL = 'https://steamspy.com/api.php?request=all&page=0'

def get_api_response(url:str):
    
    response = requests.get(url)
    
    if not response.status_code == 220:
        pass
    
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
        
def get_game_data(appid: str):
    '''Retrieves data for a single game using Steam AppID'''
    response = requests.get(f"https://steamspy.com/api.php?request=appdetails&appid={appid}")
    
    if not response.status_code == '220':
        print(response.status_code)
        # add code to handle unsucessful request later...
    
    return json.loads(response.text)

def clean_data_to_list(data: dict) -> list:
    df = pd.DataFrame(data).reset_index(drop=True)
    df.drop(['tags'], axis=1, inplace=True)
    df.drop(df.index[1:], inplace=True)
    
    return df.values.tolist()

# def to_dataframe(data: dict) -> pd.DataFrame:
#     df = pd.DataFrame(data).T
#     df.reset_index(drop=True, inplace=True)
    
#     return df
    
if __name__ == '__main__':
    data = get_api_response(API_URL)
    
    games_list = get_games_list(data)
    
    all_games_data = []
    
    for games in games_list:
        game_data = get_game_data(games)
        
        for info in clean_data_to_list(game_data):
            all_games_data.append(info)
            
        print(f"Sucessfully retrieved data for AppID: {games}")
        time.sleep(0.2)
        
    df = pd.DataFrame(all_games_data, columns=['appid', 
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
                                                'genre'])
    
    df.index += 1
    
    # Empties list to save memory
    all_games_data = None
    games_list = None
    
    df.to_csv('./csv/steamspy_game_list.csv', index_label='ownership_ranking')
