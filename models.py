from typing import Any
from sqlalchemy import create_engine
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from datetime import datetime

DEFAULT_DB = "ozon-book.db"

""" Классы """
# Base должен быть предком других моделей таблиц
class Base(DeclarativeBase): pass

class Book(Base):
    __tablename__ = 'books'

    id = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    title = mapped_column(Text, nullable=False, unique=True, index=True)
    author = mapped_column(Text)
    year_start = mapped_column(Integer)
    year_end = mapped_column(Integer)
    options = mapped_column(Text)

    isbns = relationship("ISBN", back_populates='book')
    articles = relationship("Article", back_populates='book')
    prices = relationship("Price", back_populates='book')

    def __init__(self, **kw: Any):
        # if "isbns" in kw:
        #     kw["isbns"] = []
        # if "articles" in kw:
        #     kw["articles"] = []
        super().__init__(**kw)

class ISBN(Base):
    __tablename__ = 'isbns'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id = mapped_column(Integer, ForeignKey('books.id'), index=True)
    isbn = mapped_column(Text, nullable=False, unique=True)

    book = relationship('Book', back_populates='isbns')

class Article(Base):
    __tablename__ = 'articles'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id = mapped_column(Integer, ForeignKey('books.id'), index=True)
    article = mapped_column(Text, nullable=False, unique=True)

    book = relationship('Book', back_populates='articles')

class Price(Base):
    __tablename__ = 'Prices'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id = mapped_column(Integer, ForeignKey('books.id'), index=True)
    datetime = mapped_column(DateTime, default=datetime.now)
    price = mapped_column(Integer)
    article = mapped_column(Integer)
    typeSearch = mapped_column(Text)

    book = relationship('Book', back_populates='prices')

""" Функции """
def getEngine(dbname = DEFAULT_DB, echo=False):
    # отновительный путь через :///*.db
    # абсолютный путь через :////*.db
    sqlite_db = f'sqlite:///{dbname}'
    # Создаем движок
    engine = create_engine(sqlite_db, echo=echo)
    return engine

def CreateDB(dbname = DEFAULT_DB, recreate=False, echo=False):
    if recreate: 
        import os
        if os.path.exists(dbname):
            os.remove(dbname)

    engine = getEngine(dbname=dbname, echo=echo)
    Base.metadata.create_all(bind=engine)
    engine.dispose()

def inSession(fn):
    def wrapper(*args, **kwargs):
        with Session(autoflush=False, bind=getEngine()) as db:
            kwargs['db'] = db
            fn(*args, **kwargs)
    return wrapper

def main():
    CreateDB(recreate=True)
    pass

if __name__  == '__main__':
    main()