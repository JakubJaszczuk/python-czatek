from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, DateTime
from proto.data_pb2 import User as UserProto
from datetime import datetime as dt
from security import hash_password


Base = declarative_base()


class AbstractEntity(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    creation_date = Column(DateTime, default=dt.now())


class UserEntity(AbstractEntity):
    __tablename__ = 'users'

    name = Column(String(32), nullable=False, unique=True)
    password = Column(String(64), nullable=False, unique=False)
    salt = Column(String(64), nullable=False, unique=False)

    @staticmethod
    def from_proto(user: UserProto, secure=True) -> UserEntity:
        name = user.name
        date = dt.now()
        if secure:
            password, salt = hash_password(user.password)
        else:
            password = user.password
            salt = b''
        return UserEntity(name=name, password=password, salt=salt, creation_date=date)
