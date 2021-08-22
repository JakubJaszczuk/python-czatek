from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from entity import Base
from entity import User


class Database:

    def __init__(self):
        self.engine = create_engine('sqlite:///db.db')
        Base.metadata.create_all(self.engine)

    def create_user(self, user: User):
        with Session(self.engine) as session:
            try:
                session.add(user)
                session.commit()
            except Exception:


    def log(self, message: str):
        with Session(self.engine) as session:
            session.add(message)
            session.commit()


class DatabaseCache:

    def __init__(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)

    def login_user(self):
        pass

    def log(self):
        with Session(self.persistent) as session:
            session.add(message)
            session.commit()
