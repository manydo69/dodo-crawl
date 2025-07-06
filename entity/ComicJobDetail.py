from sqlalchemy import (
    Column,
    BigInteger,
    String,
    TIMESTAMP,
    text
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ComicJobDetail(Base):
    __tablename__ = 'comic_job_detail'
    id = Column(BigInteger, primary_key=True)

    comic_website = Column(String(255), nullable=False)
    comic_url = Column(String(255), nullable=False)
    comic_folder_name = Column(String(255), nullable=False)
    status = Column(String(10))

    created_date = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_date = Column(TIMESTAMP, onupdate=text('CURRENT_TIMESTAMP'))

    def __repr__(self):
        return (
            f"<ComicJobDetail(id={self.id}, job_name='{self.comic_website}', "
            f"status='{self.status}', created_date='{self.created_date}')>"
        )