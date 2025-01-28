# from utils import createViewS
# from typing import Any
from sqlalchemy import create_engine
from sqlalchemy import Integer
from sqlalchemy import Text
# from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from datetime import datetime as dt

DEFAULT_DB = "ozon-book.db"

""" Классы """
# Base должен быть предком других моделей таблиц
class Base(DeclarativeBase): #pass
    def searchAttr(self):
        """Возвращает словарь, связанный с аттрибутом имеющего опцию QNIQEU: 
        {название: значение}"""
        pass

class Book(Base):
    __tablename__ = 'books'

    id = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    title = mapped_column(Text, nullable=False, unique=True, index=True)
    author = mapped_column(Text)
    year_start = mapped_column(Integer)
    year_end = mapped_column(Integer)
    options = mapped_column(Text)

    isbns = relationship("ISBN", back_populates='book', cascade="all, delete-orphan")
    articles = relationship("Article", back_populates='book', cascade="all, delete-orphan")
    prices = relationship("Price", back_populates='book', cascade="all, delete-orphan")

    def searchAttr(self):
        return {"title": self.title}

class ISBN(Base):
    __tablename__ = 'isbns'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id = mapped_column(Integer, ForeignKey('books.id', ondelete='CASCADE'), index=True)
    isbn = mapped_column(Text, nullable=False, unique=True)

    book = relationship('Book', back_populates='isbns')

    def searchAttr(self):
        return {"isbn": self.isbn}
    
class Article(Base):
    __tablename__ = 'articles'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id = mapped_column(Integer, ForeignKey('books.id', ondelete='CASCADE'), index=True)
    article = mapped_column(Text, nullable=False, unique=True)

    book = relationship('Book', back_populates='articles')

    def searchAttr(self):
        return {"article": self.article}
    
class Price(Base):
    __tablename__ = 'prices'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    book_id = mapped_column(Integer, ForeignKey('books.id', ondelete='CASCADE'), index=True)
    datetime = mapped_column(Text, default=dt.now().strftime("%Y-%m-%d %H:%M"))
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

def createViewS(dbname: str) -> None:
    """Создание представлений в БД"""
    from sqlalchemy import text
    with Session(autoflush=False, bind=getEngine(dbname=dbname)) as db:
        db.execute(text("""CREATE VIEW IF NOT EXISTS books_view AS
                            SELECT books.id AS book_id, 
                                title, author, year_start, year_end, options,
                                COUNT(DISTINCT isbns.isbn) AS have_isbn,
                                COUNT(DISTINCT articles.article) AS have_article
                            FROM books
                                LEFT JOIN isbns ON books.id = isbns.book_id
                                LEFT JOIN articles ON bookS.id = articles.book_id
                            GROUP BY books.id
                        """))
        db.execute(text("""CREATE VIEW IF NOT EXISTS articles_view AS
                            SELECT books.id AS book_id,
                                title, author,
                                articles.article AS article
                            FROM books
                                INNER JOIN articles ON books.id = articles.book_id;
                        """))
        db.execute(text("""CREATE VIEW IF NOT EXISTS isbns_view AS
                            SELECT books.id AS book_id,
                                title, author,
                                isbns.isbn AS isbn
                            FROM books
                                INNER JOIN isbns ON books.id = isbns.book_id;
                        """))
        db.execute(text("""CREATE VIEW IF NOT EXISTS price_view AS
                            SELECT books.id AS book_id,
                                books.title AS Title,
                                datetime, price, article, typeSearch
                            FROM prices
                                LEFT JOIN books ON prices.book_id = books.id
                       """))
        db.execute(text("""CREATE VIEW IF NOT EXISTS prices_view_min_avg AS
                            SELECT books.id AS book_id,
                                books.title AS Title,
                                MIN(price) AS min_price,
                                AVG(price) AS avg_price
                            FROM prices
                                LEFT JOIN
                                books ON prices.book_id = books.id
                            GROUP BY book_id
                       """))

def CreateDB(dbname = DEFAULT_DB, recreate=False, echo=False):
    if recreate: 
        import os
        if os.path.exists(dbname):
            os.remove(dbname)

    engine = getEngine(dbname=dbname, echo=echo)
    Base.metadata.create_all(bind=engine)
    engine.dispose()
    createViewS(dbname)

def inSession(fn):
    """Декаратор, написал, но не использовал"""
    def wrapper(*args, **kwargs):
        with Session(autoflush=False, bind=getEngine(echo=False)) as db:
            fn(*args, db=db, **kwargs)
    return wrapper

def main():
    # CreateDB(dbname='test.db', recreate=True)
    pass

if __name__  == '__main__':
    main()