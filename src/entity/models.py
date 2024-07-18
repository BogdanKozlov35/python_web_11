from sqlalchemy import Column, String, Integer, ForeignKey, Date
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    firstname = Column(String(50))
    lastname = Column(String(50))
    birthday = Column(Date)
    description = Column(String(250))

    emails = relationship("Email", back_populates="contact")
    phones = relationship("Phone", back_populates="contact")

    @hybrid_property
    def fullname(self):
        return self.firstname + " " + self.lastname


class Email(Base):
    __tablename__ = 'emails'
    id = Column(Integer, primary_key=True)
    email = Column(String(50))
    contact_id = Column(Integer, ForeignKey('contacts.id', onupdate='CASCADE'), nullable=False)
    contact = relationship('Contact', back_populates='emails')


class Phone(Base):
    __tablename__ = 'phones'
    id = Column(Integer, primary_key=True)
    phone = Column(String(20))
    contact_id = Column(Integer, ForeignKey('contacts.id', onupdate='CASCADE'), nullable=False)
    contact = relationship('Contact', back_populates='phones')
