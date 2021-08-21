# @author:
#    Mohamed Behery - mohamed.ibrahim.behery@gmail.com
#
# @description:
#   This script contains a class and its associated usage example for 
#   inserting and fetching face recognition events for the project 
#   'WEBCAM2SERVER' currently being developed and maintained by 
#   Hazem Samy - hazemsamy00@gmail.com
#
# @notes:
#   The steps for running the example code, in the end, are:
#       - installing sqlalchemy package ~ pip install SQLAlchemy
#       - installing MS SQL Server:
#           - From the following link ~ https://go.microsoft.com/fwlink/?linkid=866662
#           - choose to install SQL Server Management Studio after the installation ends.
#       - Open SSMS connect on a the pre-selected server name with Windows authentication 
#       selected by default, and then create your database with the name you desire.
#       - Use the server name and the database name from the previous step as arguments
#       for instantiating the 'database' class.


import sqlalchemy as sql
from datetime import datetime

class database:
    
    def __init__(self, server_name, db_name):
        self.engine = sql.create_engine(f'mssql+pyodbc://{server_name}/{db_name}?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
        meta = sql.MetaData()
        self.log = sql.Table(
            'log', meta,
            sql.Column('id', sql.Integer, primary_key = True),
            sql.Column('datetime', sql.DateTime),
            sql.Column('username', sql.String),
            sql.Column('image', sql.LargeBinary)
        )
        meta.create_all(self.engine)
    
    def log_event(self, username, image_bytes):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(self.log.insert().values(datetime=datetime.now() , username=username, image=image_bytes))
                return len(result.inserted_primary_key) > 0
        except:
            return -1
    
    def get_last_n_logged_events(self, n):
        try:
            with self.engine.connect() as conn:
                query = self.log.select().order_by(self.log.c.id.desc()).limit(n)
                return conn.execute(query).fetchall()
        except:
            return []

db = database('localhost', 'sample_db')
db.log_event('Mohamed Behery', b'All praises to Allah, Lord of the worlds!')
print(db.get_last_n_logged_events(5))