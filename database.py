import models
import utils
from sqlalchemy.orm import Session
from sqlalchemy import text, select

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

@models.inSession
def getBookTitle(book_id: int, db=None) -> str:
    return db.get(models.Book, book_id).title

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

def updateBook(book_id: int, book: dict, db=None, echo=False) -> None:
    """Обновить книгу по id"""
    with Session(autoflush=False, bind=models.getEngine(echo=echo)) as db:
        db.query(models.Book).filter(models.Book.id==book_id).update(book)
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

'''@models.inSession
def _getAllBooks( db=None) -> list[models.Book[models.ISBN|models.Article]]:
    """Пример возвразающий объекты. ISBNs и артикли возващаются списком объектов"""
    books = []
    all_book_obj = db.query(models.Book).all()
    for book_obj in all_book_obj:
        book_obj.isbns
        book_obj.articles
        books.append(book_obj)
    return books
# for d in _getAllBooks():
#     print(d.articles)'''

def getAllBooks(short = False, echo=False) -> list[dict]:
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
                isbns = None if isbns == [] else isbns
                articles = [a.article for a in book_obj.articles]
                articles = None if articles == [] else articles
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

def getPrices(book_id: int = None, lastdays: int = None, datetime_start = None, datetime_stop = None, getTitle = False, echo=False) -> list[dict]:
    """Принимает ID книги, а так же даты/время С и ПО какой период нужен.
    Параметр lastdays - вернуть за кол-во дней от последнего парсинга.
    Параметрт lastdays отключает datetime_start/datetime_stop
    Даты в формате datetime или '2025-12-13 12:59' 
    Без этих данных выдаст все записи в таблице.
    Возвращает список словарей"""
    def _fromdate(last_datetime, lastdays): 
        from datetime import datetime, timedelta
        last_date = datetime.strptime(last_datetime, "%Y-%m-%d %H:%M").date()
        fromdate = last_date - timedelta(hours=lastdays)
        return fromdate
    prices = []
    with Session(autoflush=False, bind=models.getEngine(echo=echo)) as db:
        # if book_id:
        result = db.query(models.Price)
        if book_id:
            result = result.filter(models.Price.book_id == book_id)
        if lastdays:
            last_datetime  = db.execute(text(f"SELECT MAX(datetime) FROM prices")).first()[0]
            result = result.filter(models.Price.datetime >= _fromdate(last_datetime, lastdays))
        else:
            if datetime_start:
                result = result.filter(models.Price.datetime >= datetime_start)
            if datetime_stop:
                result = result.filter(models.Price.datetime <= datetime_stop)
        result = result.all()

        if getTitle:
            for row in result:
                title = row.book.title
                if row.book.author:
                    title = f"{row.book.author} | {title}"
                prices.append({'book_id': row.book_id,
                        'book_title': title,
                        'datetime': row.datetime,
                        'price': row.price,
                        'article': row.article,
                        'typeSearch': row.typeSearch})
    if not getTitle:
        for row in result:
            prices.append({'book_id': row.book_id,
                    'datetime': row.datetime,
                    'price': row.price,
                    'article': row.article,
                    'typeSearch': row.typeSearch})
    return prices

def getPriceStat(echo=False) -> list[dict]:
    """Выводит статистику по книгам: последняя цена и дата, минимальняя и средняя цены. 
    Возвращает список словарей"""
    data = []
    keys = ['book_id', 'book_title', 'last_date', 'last_price', 'prev_date', 'prev_prise', 'min_price', 'avg_price']
    with Session(autoflush=False, bind=models.getEngine(echo=echo)) as db:
        last_date  = db.execute(text(f"SELECT MAX(datetime) FROM prices")).first()[0]
        for row in db.execute(text("SELECT * FROM prices_view_min_avg")).all():
            lst = list(row)
            last_prise = db.execute(text(f"SELECT MIN(price) FROM prices WHERE book_id = {lst[0]} AND datetime = '{last_date}'")).first()[0]
            prev_date = db.execute(text(f"SELECT MAX(datetime) FROM prices WHERE book_id = {lst[0]} AND datetime < '{last_date}'")).first()[0]
            prev_prise = db.execute(text(f"SELECT MIN(price) FROM prices WHERE book_id = {lst[0]} AND datetime = '{prev_date}'")).first()[0]
            author = db.execute(text(f'SELECT author FROM books WHERE id = {lst[0]}')).first()[0]
            if author:
                lst[1] = f"{author} | {lst[1]}"
            lst.insert(2, last_date)
            lst.insert(3, last_prise)
            lst.insert(4, prev_date)
            lst.insert(5, prev_prise)
            lst[-1] = round(lst[-1])
            data.append({k:v for k,v in zip(keys, lst)})
    return data

@models.inSession
def getLastPrices(book_id: int = None, db=None) -> list[dict]:
    slct = select(models.Price)
    wh = ''
    if book_id:
        slct = slct.where(models.Price.book_id == book_id) 
        wh = f'WHERE book_id = {book_id}'
    last_date  = db.execute(text(f"SELECT MAX(datetime) FROM prices {wh}")).first()[0]
    slct = slct.where(models.Price.datetime == last_date)
    data = db.scalars(slct).all()
    return [d.getDict() for d in data]

@models.inSession
def delBook(book_id: int, db=None) -> None:
    book = db.get(models.Book, book_id)
    db.delete(book)
    db.commit()

def main():
    pass

if __name__  == '__main__':
    main()