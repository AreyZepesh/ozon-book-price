import models
import utils
from sqlalchemy.orm import Session

"""TODO 
- получение данных"""

def csvToDB(csvPath: str, echo=False) -> None:
    data = utils.csvToDict(csvPath)
    for row in data:
        isbns = row.pop("isbns")
        articles = row.pop("articles")
        book = models.Book(**row)
        id = getId(book, echo=echo)
        if id:
            updateBook(id, book=row, echo=echo)
            pass
        else:
            id = addBookToDB(book=book, echo=echo)
        if isbns is not None:
            addISBN(isbns, id)
        if articles is not None:
            addArticle(articles, id)
        del id
    # getId(models.Book(title="test"))

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
            
def addBookToDB(book: models.Book, echo=False) -> int:
    """Добавить книгу в дб, вернуть ID"""
    with Session(autoflush=False, bind=models.getEngine(echo=echo)) as db:
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

def getAllBooks(echo=False) -> list:
    """Возвращает список словарей книг и их данными, isbn и артиклями"""
    books = []
    with Session(autoflush=False, bind=models.getEngine(echo=echo)) as db:
        all_book_obj = db.query(models.Book).all()
        for book_obj in all_book_obj:
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

def main():
    # csvToDB("./csv/test.csv",echo=0)
    
    # from pprint import pprint
    # pprint(getAllBooks(), sort_dicts=False)
    pass

if __name__  == '__main__':
    main()