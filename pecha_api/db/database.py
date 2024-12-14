
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


user = 'admin'
password = 'pechaAdmin'
SQLALCHEMY_DATABASE_URL = f'postgresql://{user}:{password}@localhost:5434/pecha'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()