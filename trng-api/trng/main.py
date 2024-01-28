import logging
import subprocess
import os
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, Table, MetaData, Column, DateTime, LargeBinary
from sqlalchemy import select, String, Integer, Identity
from sqlalchemy.engine.url import URL
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import TIMESTAMP

config = dict(
    drivername='driver',
    username='username',
    password='qwerty1',
    host='127.0.0.1',
    port='5000',
    database='mydb',
    query={'encoding': 'utf-8'}
)

url = URL.create(**config)

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
        return bytes(bits)[0:amount_of_bytes_needed]

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
    config = dict(database=database,
                    drivername='timescaledb',
                            host=host,
                            username=username,
                            password=password,
                            port=port)
    
    url = URL.create(**config)
    engine = create_engine(url, echo=True)
    
    metadata = MetaData()
    metadata.bind = engine
    
    # Create Tables
    random_bytes_inf_large = Table(
        'random_bytes_inf_large', metadata,
        Column("id", Integer, Identity()),
        Column('random_bytes', LargeBinary),
        Column('time', TIMESTAMP(timezone=True), default=datetime.now),
        timescaledb_hypertable={
            "time_column_name": "time",
            "chunk_time_interval": "1 hour"
        }
    )
    devices = Table(
        'devices', metadata,
        Column('device_name', String),
        Column('time', TIMESTAMP(timezone=True))
    )
    
    metadata.create_all(engine)
    
    conn = engine.connect()
        
    #Create delete procedure and job
    with open('./migrations_job/delete_procedure.sql', 'r') as prod, open('./migrations_job/delete_job.sql', 'r') as job:
        sql_commands = [prod.read(), job.read()]
        
        for command in sql_commands:
            conn.execute(text(command))
            conn.commit()
        
    iterations = 0
    while True:
        now = datetime.now()
        
        random_bytes = GetBytes._get_random_payload(amount_of_bytes_needed=1024*1024)
    
        # Insert new row
        insert_bytes_sql = random_bytes_inf_large.insert().values({"time": now, "random_bytes": random_bytes})
        conn.execute(insert_bytes_sql)
        
        # 180 ~ approximate 1 hour
        if iterations % 180 == 0:
            device_name = GetBytes.list_devices()
            insert_device = devices.insert().values({"time": now, "device_name": str(device_name)})
            conn.execute(insert_device)
        
        conn.commit()
        iterations+=1