import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *

def process_song_file(cur, filepath):
    """Read song JSON data and populate songs and artists table
    
    Parameters:
    cur (psycopg2.extensions.cursor): Database Cursor
    filepath (str): The path of the song JSON file
    
    """
    
    # open song file
    df = pd.read_json(filepath, lines=True)

    # insert song record
    song_data = df[["song_id", "title", "artist_id", "year", "duration"]].values[0].tolist()
    cur.execute(song_table_insert, song_data)
    
    # insert artist record
    artist_data = df[["artist_id", "artist_name", "artist_location", "artist_latitude", "artist_longitude"]].values[0].tolist()
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    """Read log data and populate the dimension tables
    
    Parameters:
    cur (psycopg2.extensions.cursor): Database Cursor
    filepath (str): The path of the log JSON file
    
    """
    
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df['page'] == 'NextSong']

    # convert timestamp column to datetime
    t = pd.to_datetime(df['ts'], unit='ms')
    
    # Extract the timestamp, hour, day, week of year, month, year, and weekday informaton
    time_data = []
    ts_list = df['ts'].tolist()
    hour_list = t.dt.hour.tolist()
    day_list = t.dt.day.tolist()
    week_list = t.dt.week.tolist()
    month_list = t.dt.month.tolist()
    year_list = t.dt.year.tolist()
    weekday_list = t.dt.day_name().tolist()
    for index, time_item in enumerate(ts_list):
        time_data.append([time_item, hour_list[index], day_list[index], week_list[index], month_list[index], year_list[index], weekday_list[index]])
    
    # Specify labels for these columns
    column_labels = ('start_time', 'hour', 'day', 'week', 'month', 'year', 'weekday')
    
    # Create a dataframe containing the time data for this file
    time_df = pd.DataFrame(time_data, columns = column_labels)

    # insert time data records
    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[["userId", "firstName", "lastName", "gender", "level"]]

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():
        
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = (row.ts, row.userId, row.level, songid, artistid, row.sessionId, row.location, row.userAgent)
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    """Read file names from song and log directory and process them by using the provided functions
    
    Parameters:
    cur: Database cursor
    conn: Database connection
    filepath (str): Directory of the JSON files
    func: Function that processes the dataset
    
    """
    
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()