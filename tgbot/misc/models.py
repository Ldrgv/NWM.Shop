from sqlalchemy import Column, BigInteger, String, Integer, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Payment(Base):
    __tablename__ = "payments"

    product = Column(String(50))
    user_id_time = Column(String(50), primary_key=True)


class Product(Base):
    __tablename__ = "products"

    key = Column(String(50), primary_key=True)
    title = Column(String(50))
    description = Column(String(255))
    price = Column(Integer)
    photo_url = Column(String(1023))
    need_name = Column(Boolean)
    need_phone_number = Column(Boolean)
    need_email = Column(Boolean)
    need_shipping_address = Column(Boolean)


class Discount(Base):
    __tablename__ = "discounts"

    user_id = Column(BigInteger, primary_key=True)
    product = Column(String(50))
    discount = Column(Integer)


class FullPackUser(Base):
    __tablename__ = "full_pack_users"

    user_id = Column(BigInteger, primary_key=True)
    user_name = Column(String(128))


class Misc(Base):
    __tablename__ = "misc"

    key = Column(String(50), primary_key=True)
    value = Column(String(50))
