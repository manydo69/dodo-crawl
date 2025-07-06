import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from entity.ComicJobDetail import ComicJobDetail, Base

# Load environment variables
load_dotenv()

# Get database connection details from environment variables
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_NAME = os.environ.get("DB_NAME")

# Create database URL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """
    Get a database session.
    
    Returns:
        Session: SQLAlchemy session
    """
    session = SessionLocal()
    try:
        return session
    except Exception as e:
        session.close()
        raise e

def get_new_comic_jobs():
    """
    Get all comic jobs with status "NEW".
    
    Returns:
        list: List of ComicJobDetail objects with status "NEW"
    """
    session = get_db_session()
    try:
        return session.query(ComicJobDetail).filter(ComicJobDetail.status == "NEW").all()
    finally:
        session.close()

def update_comic_job_status(job_id, status):
    """
    Update the status of a comic job.
    
    Args:
        job_id (int): ID of the comic job
        status (str): New status ("PROCESSING", "COMPLETED", "FAILED")
    
    Returns:
        bool: True if update was successful, False otherwise
    """
    session = get_db_session()
    try:
        job = session.query(ComicJobDetail).filter(ComicJobDetail.id == job_id).first()
        if job:
            job.status = status
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error updating job status: {e}")
        return False
    finally:
        session.close()