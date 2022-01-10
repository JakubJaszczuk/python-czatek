from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from entity import Base, UserEntity
from typing import Optional


class Database:

    def __init__(self):
        self.engine = create_engine('sqlite:///db.db')
        Base.metadata.create_all(self.engine)

    def create_user(self, user: UserEntity) -> bool:
        with Session(self.engine) as session:
            try:
                session.add(user)
                session.commit()
                return True
            except Exception:
                return False

    def get_user_by_name(self, username: str) -> Optional[UserEntity]:
        with Session(self.engine) as session:
            return session.query(UserEntity).filter_by(name=username).first()

    def log(self, message: str):
        with Session(self.engine) as session:
            session.add(message)
            session.commit()
