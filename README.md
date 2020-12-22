# Introduction
Sparkify is a startup company. They developed a music streaming app. From this app they are collecting the songs and user activity information in JSON format. Our task in this project is to design a Postgres database to store these information. The Sparkify analytics team will use this database to fullfil their analytical goals.

# Database schema design
We collect information from two datasets.

1. Song Dataset: Provides song and artist information.
2. Log Dataset: Provides user activities information.

From these information, we created a star schema by using the following tables:

## Fact Table
### songplays

    CREATE TABLE IF NOT EXISTS songplays
    (
        songplay_id SERIAL PRIMARY KEY,
        start_time bigint,
        user_id int,
        level varchar, 
        song_id varchar, 
        artist_id varchar, 
        session_id int,
        location varchar, 
        user_agent varchar
    )


## Dimension Tables
### users

    CREATE TABLE IF NOT EXISTS users
    (
        user_id int PRIMARY KEY,
        first_name varchar, 
        last_name varchar, 
        gender varchar, 
        level varchar
    )

### songs

    CREATE TABLE IF NOT EXISTS songs
    (
        song_id varchar PRIMARY KEY,
        title varchar,
        artist_id varchar,
        year int,
        duration float8
    )

### artists

    CREATE TABLE IF NOT EXISTS artists
    (
        artist_id varchar PRIMARY KEY,
        name varchar,
        location varchar,
        latitude float8,
        longitude float8
    )

### time

    CREATE TABLE IF NOT EXISTS time
    (
        start_time bigint PRIMARY KEY,
        hour smallint,
        day smallint,
        week smallint,
        month smallint,
        year smallint,
        weekday varchar
    )

By using the start schema, we can perform fast aggregations with simplifies queries.

# ETL pipeline
In this project, we created an ETL pipeline (etl.py) that reads the song and log datasets and loads them into the above tables. The steps that are performed in this script are described in the Jupyter Notebook etl.ipynb

Befor executing the ETL pipeline script, we reset the tables by using the create_tables.py script.

    python create_tables.py

We can then execute the ETL pipeline script

    python etl.py

To check the data in tables, we use  the Jupyter Notebook test.ipynb

All database queries are defined in sql_queries.py script. These queries are used by both etl.ipynb and etl.py scripts.

In the ETL pipeline, we insert in each table one row at a time. For the limited set of data, the script is fast. But when we'll try to insert a big amout of data, it is better to consider the bulk insert method.

# Purpose of the database
The database can be used to answer various business queries. Here are some examples:

- Whate are the top 3/10/100 songs for a specific day/week/month? This information can be used to advertise the top songs.
- Which songs are frequently played by a free user and how many times? This can be used to recommend the songs to the users.
- After a specific song, which song is played? This can be also used by the recommendation system.
- Which artist's songs are listened by the paid users? This may help to provide incentive payments to the artists.
- What is the peak time of listening musing? It can be analyzed daily, weekly and monthly basis.
- What songs users are currently listening to? If we execute the ETL pipeline more frequently, it is possible to get this information almost in real time. However, it is still a batch process. So, the information cannot be live and depends on the execution time of the last batch.

Here are some purposes of the database:

- To advertise songs and artists to the users.
- To recommend the songs to the user.
- To determine the peak usage of the application.