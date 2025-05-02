# from utils import createViewS
# from typing import Any
from typing import Any
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
    __table_args__ = {'sqlite_autoincrement': True}
    def searchAttr(self) -> dict:
        """Возвращает словарь, связанный с аттрибутом имеющего опцию QNIQEU: 
        {название: значение}"""
        pass

    def getDict(self) -> dict:
        """Возвращает словарь с аттрибутами объекта"""
        dct = vars(self).copy()
        # Убираем рабочую инфу алхимии
        del dct['_sa_instance_state']
        # Для НЕ книг - запрос названия и автора книг, удаление id
        if dct.get('book_id'):
            if dct.get('book'):
                dct['author'] = self.book.author
                dct['title'] = self.book.title
                del dct['book']
            del dct['id']
        if dct.get('options'):
            from utils import strToLst
            dct['options'] = strToLst(dct.get('options'))
        isbns = dct.get('isbns')
        if isbns and isbns != []:
            dct['isbns'] = [i.isbn for i in isbns]
            # dct['isbns'] = [i.isbn for i in isbns if isinstance(i, ISBN)]
        articles = dct.get('articles')
        if articles and articles != []:
            dct['articles'] = [a.article for a in articles]
            # dct['articles'] = [a.article for a in articles if isinstance(a, Article)]
        return dct

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
    datetime = mapped_column(Text, default=dt.now().strftime("%Y-%m-%d %H:%M"), index=True)
    price = mapped_column(Integer, index=True)
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
        db.execute(text("""CREATE VIEW prices_view_all AS
                            SELECT books.id AS book_id,
                                books.title,
                                books.author,
                                prices.datetime,
                                prices.price,
                                prices.article,
                                prices.typeSearch
                            FROM prices
                                LEFT JOIN
                                books ON books.id = prices.book_id
                            ORDER BY prices.datetime DESC;
                       """))
        db.execute(text("""CREATE VIEW prices_view_current AS
                            SELECT books.id AS book_id,
                                CASE WHEN books.author NOT NULL THEN books.author || " | " || books.title WHEN books.author IS NULL THEN books.title END AS book_title,
                                prices.datetime AS last_date,
                                prices.price AS last_price,
                                prices.article,
                                prices.typeSearch
                            FROM books
                                LEFT JOIN
                                prices ON prices.book_id = books.id AND 
                                            prices.datetime = (SELECT MAX(datetime) FROM prices);
                       """))
        db.execute(text("""CREATE VIEW prices_view_min_avg AS
                            SELECT books.id AS book_id,
                                books.title AS Title,
                                MIN(price) AS min_price,
                                CAST (ROUND(AVG(price) ) AS INTEGER) AS avg_price
                            FROM prices
                                LEFT JOIN
                                books ON prices.book_id = books.id
                            WHERE prices.datetime < (SELECT MAX(prices.datetime)FROM prices)
                            GROUP BY book_id;
                       """))
        db.execute(text("""CREATE VIEW prices_view_prev AS
                            SELECT books.id AS book_id,
                                CASE 
                                    WHEN books.author NOT NULL THEN books.author || " | " || books.title 
                                    WHEN books.author IS NULL THEN books.title 
                                END AS book_title,
                                _prices.datetime AS prev_date,
                                _prices.price AS prev_price,
                                _prices.article,
                                _prices.typeSearch
                            FROM books
                                LEFT JOIN
                                (SELECT book_id, MAX(datetime) AS datetime,
                                        price, article, typeSearch
                                    FROM prices
                                    WHERE prices.datetime < (SELECT MAX(datetime) FROM prices)
                                    GROUP BY book_id, typeSearch
                                )
                                AS _prices ON _prices.book_id = books.id;
                       """))
        db.execute(text("""CREATE VIEW prices_stat AS
                            SELECT prices_view_current.book_id,
                                prices_view_current.book_title,
                                prices_view_current.last_date,
                                MIN(prices_view_current.last_price) AS last_price,
                                prices_view_prev.prev_date,
                                MIN(prices_view_prev.prev_price) AS prev_price,
                                prices_view_min_avg.min_price,
                                prices_view_min_avg.avg_price
                            FROM prices_view_current
                                LEFT JOIN
                                prices_view_prev USING (
                                    book_id
                                )
                                LEFT JOIN
                                prices_view_min_avg USING (
                                    book_id
                                )
                            GROUP BY book_id
                            ORDER BY prev_date IS NULL AND 
                                    last_date IS NULL NULLS LAST;
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
            return fn(*args, db=db, **kwargs)
    return wrapper

def main():
    # CreateDB(dbname='test.db', recreate=True)
    pass

if __name__  == '__main__':
    main()