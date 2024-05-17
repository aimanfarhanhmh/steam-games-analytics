import json
import requests
import pandas as pd
from pathlib import Path

API_URL = 'https://steamspy.com/api.php?request=all&page=0'

def get_api_response(url:str):
    
    response = requests.get(url)
    
    if not response.status_code == 220:
        pass
    
    return json.loads(response.text)

def to_dataframe(data: dict) -> pd.DataFrame:
    df = pd.DataFrame(data).T
    df.reset_index(drop=True)
    
    return df

def create_game_list(list: list) -> None:
    
    file_path = Path('./games_list.txt')
    with open(file_path, 'w') as file_gameslist:
        file_gameslist.writelines(f"{app_id}\n" for app_id in list)
    
if __name__ == '__main__':
    data = get_api_response(API_URL)
    
    df = to_dataframe(data)
    games_list = df['appid'].values.tolist()
    
    create_game_list(games_list)
    
    csv_path = Path('./csv/steamspy_owner_list.csv')
    df.to_csv(csv_path, index_label='ownership_rank')