import sqlalchemy
import pandas as pd
from sqlalchemy.orm import sessionmaker
import requests
import json
from datetime import datetime
import datetime
import sqlite3

DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"
USER_ID = "tonbotomoe"
TOKEN = "BQBcDMTh09_bFLY5S_FZnkyMCEX3k_YizaS_YIoACvLCMlWT-mv65hPHxWE95nGLfSYn_WAup3EjUX9Bs6w2OzW_W1i1tmtuNDvCDnyx12it7C1ICZkP7e3fjklbxeVnHdJ_sZuf3Vg7ij3junaA"

# Generate token periodically here: https://developer.spotify.com/console/get-recently-played/

def check_if_valid_data(df:pd.DataFrame) -> bool:
    #check if dataframe is empty
    if df.empty:
        print("No songs downloaded. Finishing execution...")
        return False

    # primary key for dataframe is the variable played_at
    # primary key check
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception("Primary Key Check is violated.")
    
    # check for nulls
    if df.isnull().values.any():
        raise Exception("Null values found.")

    # Check that all timestamps are of yesterday's date
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday = yesterday.replace(hour=0,minute=0,second=0,microsecond=0)

    timestamps = df['timestamp'].tolist()
    for timestamp in timestamps:
        if datetime.datetime.strptime(timestamp,"%Y-%m-%d") != yesterday:
            raise Exception("At least one song wasn't played within 24 hours ago.")
    





if __name__ == "__main__":

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {token}".format(token=TOKEN)
    }

    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)   
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000
    today_unix_timestamp = int(today.timestamp()) * 1000

    r = requests.get("https://api.spotify.com/v1/me/player/recently-played?after={time}".format(time=yesterday_unix_timestamp),headers = headers)

    data=r.json()
    print(data)

    # only need this fields from Spotify data
    song_names = []
    artist_names = []
    played_at_list = []
    timestamps = []

    # look at .json file. need to see the structure to get info
    for song in data["items"]:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][0:10])

    song_dict = {
        "song_name": song_names,
        "artist_name": artist_names,
        "played_at": played_at_list,
        "timestamp": timestamps,
    }

    song_df = pd.DataFrame(song_dict, columns = ["song_name","artist_name","played_at","timestamp"])

    # Validate
    if check_if_valid_data(song_df):
        print("Data is valid. Proceed to load stage")

    print(song_df)