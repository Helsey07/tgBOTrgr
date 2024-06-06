import psycopg2
import asyncpg

async def connect_to_db():
    try:
        connection = await asyncpg.connect(
            host='127.0.0.1',
            port='5432',
            database='tgbot',
            user='postgres',
            password='egor2003'
        )
        return connection

    except psycopg2.OperationalError as e:
        print(f"Could not connect to the database: {e}")
        return None

