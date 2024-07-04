from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username = Column(String, unique=True, nullable=False)

class Item(Base):
    __tablename__ = 'items'
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
