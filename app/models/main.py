from sqlalchemy import Column, String, Integer, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base

Model = declarative_base()


class User(Model):
    __tablename__ = "users"

    c_id = Column("id", Integer, primary_key=True)
    c_username = Column("username", String(20))
    c_email = Column("email", String)
    c_password = Column("password", String(60))
    c_join = Column("join", DateTime)

    c_twi_id = Column("twi_id", Integer)
    c_twi_token = Column("twi_token", String(60))
    c_twi_secret = Column("twi_secret", String(120))
    c_twi_max = Column("twi_max", BigInteger)
    c_twi_since = Column("twi_since", BigInteger)

    c_wei_id = Column("wei_id", Integer)
    c_wei_token = Column("wei_token", String(60))
    c_wei_max = Column("wei_max", BigInteger)
    c_wei_since = Column("wei_since", BigInteger)

    def __repr__(self):
        return "<User: %s, join at %s>" % (self.c_username, str(self.c_join))
