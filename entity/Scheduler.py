from sqlalchemy import (
    Column,
    BigInteger,
    String,
    TIMESTAMP,
    text
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Scheduler(Base):
    __tablename__ = 'scheduler'
    id = Column(BigInteger, primary_key=True)

    job_name = Column(String(255), nullable=False)
    status = Column(String(10))

    created_date = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_date = Column(TIMESTAMP, onupdate=text('CURRENT_TIMESTAMP'))

    def __repr__(self):
        return (
            f"<Scheduler(id={self.id}, job_name='{self.job_name}', "
            f"status='{self.status}', created_date='{self.created_date}')>"
        )
