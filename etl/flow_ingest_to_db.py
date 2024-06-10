import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

steamweb_path = Path(__file__).parent / 'staging/steamweb_games.csv'
steamspy_path = Path(__file__).parent / 'staging/steamspy_games.csv'

# Postgresql Configs
user = 'root'
password = 'root'
host = 'localhost'
port = '5432'
db = 'steam_game_analytics'

def ingest_postgres(path:Path|str, table_name:str):
    
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    df = pd.read_csv(path)
    df.to_sql(name=table_name, con=engine, if_exists='replace')


if __name__ == '__main__':
    ingest_postgres(steamweb_path, 'steamweb_data')
    ingest_postgres(steamspy_path, 'steamspy_data')