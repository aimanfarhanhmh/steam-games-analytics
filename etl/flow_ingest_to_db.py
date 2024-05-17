import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

csv_path = Path('./csv/steamapi_games_list.csv')

# Postgresql Configs
user = 'root'
password = 'root'
host = 'localhost'
port = '5432'
db = 'steam_game_analytics'

engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

df = pd.read_csv(csv_path)

df.to_sql(name='steam_data', con=engine, if_exists='append')