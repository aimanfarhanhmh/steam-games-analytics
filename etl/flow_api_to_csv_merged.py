import requests
import time
import pandas as pd
from pathlib import Path

SLEEP_TIME = 0.2

def get_api_response(url:str, params:dict) -> dict:
    response = requests.get(url, params=params)
    return response.json()

def get_games_list(df:pd.DataFrame) -> Path:
    
    array_appid = df['appid'].values
    file_path = Path(__file__).parent / 'games_list.txt'
    with open(file_path, 'w') as file_gameslist:
        file_gameslist.writelines(f"{app_id}\n" for app_id in array_appid)
        
    return file_path

def write_staging_local(df: pd.DataFrame, filename: str, columns: list = None) -> None:
    
    file_path = Path(__file__).parent / 'staging' / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if columns:
        df.to_csv(file_path, index=False, columns=columns)
    else:
        df.to_csv(file_path, index=False)
        
    print(f"Sucessfully exported to {file_path}")

def flow_steamspy_api_to_csv(export_gamelist:bool = False) -> None:
    json_response = get_api_response("https://steamspy.com/api.php", {"request": "all", 'page':'0'}) # Get first page of data (Top 1000 games)
    df = pd.DataFrame(json_response).T
    
    if export_gamelist:
        print(f'Exported game list to: {get_games_list(df)}')

    write_staging_local(df, 'steamspy_games.csv')
    
    # csv_path = Path('./staging/steamspy_games.csv')
    # csv_path = Path(__file__).parent / 'staging/steamspy_games.csv'
    # csv_path.parent.mkdir(parents=True, exist_ok=True)
    # df.to_csv(csv_path, index=False)
    
def flow_steamweb_api_to_csv(import_gamelist:bool = False) -> None:
    pass
    
if __name__ == "__main__":
    flow_steamspy_api_to_csv(export_gamelist=True)