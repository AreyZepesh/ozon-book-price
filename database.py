import models
import utils
from sqlalchemy.orm import Session

def csvToDB(csvPath: str, echo=False) -> None:
    data = utils.csvToDict(csvPath)
    for row in data:
        isbns = row.pop("isbns")
        articles = row.pop("articles")
        id = getBookId(row['title'], echo=echo)
        if id:
            updateBook(id, book=row, echo=echo)
        else:
            id = addBookToDB(book=row, echo=echo)
        if isbns is not None:
            addISBN(isbns, id)
        if articles is not None:
            addArticle(articles, id)
        del id

def getBookId(book_title: str, echo=False) -> int|None:
    """Вернуть ID, если книга есть в базе"""
    with Session(autoflush=False, bind=models.getEngine(echo=echo)) as db:
        foo = db.query(models.Book).filter(models.Book.title == book_title).first()
    if foo is not None:
        return foo.id
    else:
        return None
            
def getId(obj, echo=False) -> int|None:
    """Вернуть ID, если есть в базе.
    Принимает объект, имеющий атрибут UNIQEU,
      из любой модели таблиц БД (models.py)"""
    with Session(autoflush=False, bind=models.getEngine(echo=echo)) as db:
        foo = db.query(obj.__class__).filter_by(**obj.searchAttr()).first()
    if foo is not None:
        return foo.id
    else:
        return None
            
def addBookToDB(book: dict, echo=False) -> int:
    """Добавить книгу в дб, вернуть ID.
    Получает словарь книги, ключи: 
    ['title','author','year_start','year_end','options']"""
    with Session(autoflush=False, bind=models.getEngine(echo=echo)) as db:
        book = models.Book(**book)
        db.add(book)
        db.commit()
        db.refresh(book)
    return book.id

def updateBook(id: int, book: dict, db=None, echo=False) -> None:
    """Обновить книгу по id"""
    with Session(autoflush=False, bind=models.getEngine(echo=echo)) as db:
        db.query(models.Book).filter(models.Book.id==id).update(book)
        db.commit()

def addISBN(isbns: list, book_id: int, echo=False) -> None:
    """Добавить ISBN если нет в базе"""
    with Session(autoflush=False, bind=models.getEngine(echo=echo)) as db:
        for i in isbns:
                if db.query(models.ISBN).filter(models.ISBN.isbn==i).first() is None:
                    db.add(models.ISBN(book_id=book_id, isbn=i))
        db.commit()

def addArticle(articles: list, book_id: int, echo=False) -> None:
    """Добавить артикль если нет в базе"""
    with Session(autoflush=False, bind=models.getEngine(echo=echo)) as db:
        for a in articles:
            if db.query(models.Article).filter(models.Article.article==a).first() is None:
                db.add(models.Article(book_id=book_id, article=a))
        db.commit()

def getAllBooks(short = False, echo=False) -> list:
    """Возвращает список словарей книг и их данными, isbn и артиклями/
    Если указать short - вернет только ID и название"""
    books = []
    with Session(autoflush=False, bind=models.getEngine(echo=echo)) as db:
        all_book_obj = db.query(models.Book).all()
        for book_obj in all_book_obj:
            if short:
                books.append({'id': book_obj.id,
                            'title': book_obj.title})
            else:
                isbns = [i.isbn for i in book_obj.isbns]
                articles = [a.article for a in book_obj.articles]
                books.append({'id': book_obj.id,
                            'title': book_obj.title,
                            'author': book_obj.author,
                            'year_start': book_obj.year_start,
                            'year_end': book_obj.year_end,
                            'isbns': isbns,
                            'articles': articles,
                            'options': utils.strToLst(book_obj.options)})
    return books

def addPrice(data: dict, echo=False) -> None:
    """Принимает словарь, в котором:
    {'book_id': int,
    'datetime': datetime,
    'price': int,
    'article': int,
    'typeSearch': str}"""
    with Session(autoflush=False, bind=models.getEngine(echo=echo)) as db:
        price = models.Price(**data)
        db.add(price)
        db.commit()

def getPrices(book_id: int = None, datetime_start = None, datetime_stop = None, echo=False) -> list:
    """Принимает ID книги, а так же даты/время С и ПО какой период нужен.
    Даты в формате datetime или '2025-12-13 12:59' 
    Без этих данных выдаст все записи в таблице.
    Возвращает список словарей"""
    prices = []
    with Session(autoflush=False, bind=models.getEngine(echo=echo)) as db:
        # if book_id:
        result = db.query(models.Price)
        if book_id:
            result = result.filter(models.Price.book_id == book_id)
        if datetime_start:
            result = result.filter(models.Price.datetime >= datetime_start)
        if datetime_stop:
            result = result.filter(models.Price.datetime <= datetime_stop)
        result = result.all()
    for row in result:
        prices.append({'book_id': row.book_id,
                       'datetime': row.datetime,
                       'price': row.price,
                       'article': row.article,
                       'typeSearch': row.typeSearch})
    return prices






def main():
    # csvToDB("./csv/test.csv",echo=0)
    pass

if __name__  == '__main__':
    main()