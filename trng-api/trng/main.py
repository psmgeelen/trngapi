import logging
import subprocess
import os
from datetime import datetime
import psycopg2

class GetBytes(object):

    @staticmethod
    def _get_random_payload(
        amount_of_bytes_needed: int,
    ) -> bytearray:
        p = subprocess.Popen("infnoise", stdout=subprocess.PIPE)
        # Get bytes
        bits = bytearray()
        stop = False
        while not stop:
            bits += bytearray(p.stdout.readline(1024))
            if len(bits) > amount_of_bytes_needed:
                stop = True
        return bits

    @staticmethod
    def list_devices():
        p = subprocess.run(["infnoise", "-l"], stdout=subprocess.PIPE)
        return p.stdout

if __name__ == "__main__":

    # Get Credentials DB
    username = os.environ["DB_USERNAME"]
    password = os.environ["DB_PASSWORD"]
    host = os.environ["DB_HOST"]
    port = os.environ["DB_PORT"]
    database = os.environ["DB_NAME"]

    print(os.environ)

    # connect to DB
    conn = psycopg2.connect(database=database,
                            host=host,
                            user=username,
                            password=password,
                            port=port)
    cursor = conn.cursor()

    # Init DB
    cursor.execute("""CREATE TABLE IF NOT EXISTS public.random_bytes_inf (
        time TIMESTAMPTZ NOT NULL,
        random_bytes BYTEA,
        PRIMARY KEY(time));""")
    cursor.execute("""SELECT create_hypertable('public.random_bytes_inf', 'time');""")
    # Write device name to DB

    while True:
        random_bytes = GetBytes._get_random_payload(amount_of_bytes_needed=128)
        print(random_bytes)
        now = datetime.datetime.now()
        print(now)
        insert_sql = psycopg2.sql.SQL("INSERT INTO public.random_bytes_inf (time, random_bytes) VALUES (%s, %s);")
        cursor.execute(insert_sql, (now, random_bytes))
