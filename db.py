__author__ = 'RiteshReddy'
import __setup_path
from sqlalchemy import create_engine, MetaData

engine = create_engine("mysql://root:root@localhost/drcc", echo=False)
metadata = MetaData(bind=engine)

#print engine.execute('select * from users').fetchall()