import models
import utils
from sqlalchemy.orm import Session

"""TODO 
- добавление одной книги, тремя аргументами (словарь, список, список)
- в создание таблицы - реплейс для уников
- вифки
- получение данных"""

def csvToDB(csvPath):
    data = utils.csvToDict(csvPath)
    for row in data:
        isbns = row.pop("isbns")
        articles = row.pop("articles")
        book = models.Book(**row)
        # addBookToDB(book, articles, isbns)
        isExist(book)
    # isExist(models.Book(title="test"))
            
def addBookToDB(book: models.Book, isbns: list, articles: list, echo=False):
    with Session(autoflush=False, bind=models.getEngine(echo=echo)) as db:
        db.add(book)
        db.commit()
        db.refresh(book)
        if isbns is not None:
            for i in isbns:
                db.add(models.ISBN(book_id=book.id, isbn=i))
        if articles is not None:
            for a in articles:
                db.add(models.Article(book_id=book.id, article=a))
        db.commit()

def isExist(book: models.Book, echo=False):
    with Session(autoflush=False, bind=models.getEngine(echo=False)) as db:
        # print(book.title)
        foo = db.query(models.Book).filter(models.Book.title==book.title).first()
        print(foo)


# @models.inSession
# def testWrapper(**kwargs):
#     db = kwargs['db']
#     book = db.query(models.Book).first()
#     print(book.id, book.title)


def main():
    csvToDB("./csv/test.csv")
    # exist_in_DB()
    pass

if __name__  == '__main__':
    main()