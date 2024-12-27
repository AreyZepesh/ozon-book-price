from sqliteDB import getISBNs, getArticles

class Book:
    def __init__(self, title, author = "", year_start = "", year_end = "", **kwargs) -> None:
        # TODO издатель - возвращать id если есть в базе
        """Рекомендуемые переменные, которые взаимодействуют с БД / 
        Recommended variables that interact with the database:
        **kwargs: dict = {
        'publisher': str(), 
        'publisher_ozon_id': int(), 
        'isbnS': list(), 
        'articleS': list()}
        
        Эти данные будут вставлены в БД. Идентификатор книги возвращается из БД автоматически /
        This data will be inserted to DB. Book's ID returned from DB automatically
        """

        self.title: str = title
        self.author: str = author
        self.year_start: int = year_start
        self.year_end: int = year_end

        self._kwargs = kwargs

        # self.publisher: int = publisher 
        # self.publisher_ozon_id: int = publisher_ozon_id 

        # ['id', 'title', 'author', 'year_start', 'year_end', 'publisher', 'publisher_ozon_id', 'have_isbn', 'have_article']
        # self.id: int = book_id
        # if 'have_isbn' in self._kwargs.keys():
        #     if self._kwargs['have_isbn'] > 0:
        #         self.isbnS = getISBNs(self.id)
        # else:
        #     self.isbnS = []

        # if 'have_article' in self._kwargs.keys():
        #     if self._kwargs['have_article'] > 0:
        #         self.articleS = getArticles(self.id)
        # else:
        #     self.articleS = []

dick = dict(title = 'test', author = "author", year_start = "st", year_end = "end", publisher = "ast", publisher_ozon_id = "2025", have_isbn = 3, have_article = 2)
a = Book(**dick)
print(a.title)
print(vars(a))