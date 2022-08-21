from sqlalchemy import Column, BigInteger, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Payment(Base):
    __tablename__ = "payments"

    product = Column(String(50))
    user_id_time = Column(String(50), primary_key=True)


class Price(Base):
    __tablename__ = "prices"

    product = Column(String(50), primary_key=True)
    price = Column(Integer)


class Discount(Base):
    __tablename__ = "discounts"

    user_id = Column(BigInteger, primary_key=True)
    product = Column(String(50))
    discount = Column(Integer)


class FullPackUser(Base):
    __tablename__ = "full_pack_users"

    user_id = Column(BigInteger, primary_key=True)
    user_name = Column(String(128))
    chat_id = Column(BigInteger)
