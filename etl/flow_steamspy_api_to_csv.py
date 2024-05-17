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
    
if __name__ == '__main__':
    data = get_api_response(API_URL)
    df = pd.DataFrame(data).T.reset_index(drop=True)
    
    games_list = df['appid'].values.tolist()
    
    with open('./games_list.txt', 'w') as file_gamelist:
        for appid in games_list:
            file_gamelist.write(str(appid) + '\n')
    
    csv_path = Path('./csv/steamspy_owner_list.csv')
    
    df.to_csv(csv_path, index_label='ownership_rank')