from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# url for SQLite (development)
SQLALCHEMY_DATABASE_URL = "sqlite:///./crud_senac.db"

# For PostgreSQL it would be something like:
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Apenas para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()