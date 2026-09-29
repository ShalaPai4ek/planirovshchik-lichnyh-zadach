from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DATABASE_URL = "mysql+pymysql://plans_user:plans_password@db:3306/plans"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine
)


class Base(DeclarativeBase):
    pass
