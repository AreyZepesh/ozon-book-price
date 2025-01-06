import models
import utils
# from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

    # Создаем класс сессии
    # SESSION = sessionmaker(autoflush=False, bind=ENGINE)

"""TODO 
- добавление одной книги, тремя аргументами (словарь, список, список)
- в создание таблицы - реплейс для уников
- вифки
- получение данных"""

def csvToDB(csvPath):
    engine = models.getEngine()


    data = utils.csvToDict(csvPath)

    with Session(autoflush=False, bind=engine) as db:
        for row in data:
            isbns = row.pop("isbns")
            articles = row.pop("articles")
            book = models.Book(**row)
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
        pass

def main():
    csvToDB("test.csv")
    pass

if __name__  == '__main__':
    main()