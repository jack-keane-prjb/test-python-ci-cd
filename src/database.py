import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base

# from sqlalchemy.orm import sessionmaker


def get_db_url():

    if "PYTEST_CURRENT_TEST" in os.environ:
        return "sqlite+aiosqlite:///:memory:"
    else:
        return "sqlite+aiosqlite:///./app.py.db"


DATABASE_URL = get_db_url()
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
Base = declarative_base()
session = async_session()
