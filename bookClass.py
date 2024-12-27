from sqliteDB import getISBNs, getARTICLEs

class Book:
    def __init__(self, book_id, title, author = "", year_start = "", year_end = "", publisher = "", publisher_ozon_id = "", **kwargs) -> None:
        # ['id', 'title', 'author', 'year_start', 'year_end', 'publisher', 'publisher_ozon_id', 'have_isbn', 'have_article']
        self.id: int = book_id
        self.title: str = title
        self.author: str = author
        self.year_start: int = year_start
        self.year_end: int = year_end
        self.publisher: int = publisher 
        self.publisher_ozon_id: int = publisher_ozon_id 
        self._kwargs = kwargs

        if 'have_isbn' in self._kwargs.keys():
            if self._kwargs['have_isbn'] > 0:
                self.isbnS = getISBNs(self.id)
        else:
            self.isbnS = []

        if 'have_article' in self._kwargs.keys():
            if self._kwargs['have_article'] > 0:
                self.articleS = getARTICLEs(self.id)
        else:
            self.articleS = []

dick = dict(book_id = 1, title = 'test', author = "author", year_start = "st", year_end = "end", publisher = "ast", publisher_ozon_id = "2025", have_isbn = 3, have_article = 2)
a = Book(**dick)
print(a.id, a.title, a.articleS, a.isbnS)
print(vars(a))