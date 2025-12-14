from library.repositories.base_repository import BaseRepository
from library.models.book import Book
from library.models.author import Author
from library.models.category import Category
from sqlalchemy import or_


class BookRepository(BaseRepository):
    def __init__(self):
        super().__init__(Book)

    def search(self, query):
        """Kitap adı, yazar, kategori veya barkoda göre arama yapar"""
        if not query:
            return self.get_all()

        return self.model.query.join(Author).join(Category).filter(
            or_(
                self.model.name.contains(query),
                Author.name.contains(query),
                Category.name.contains(query),
                self.model.barcode.contains(query)
            )
        ).all()

    def find_by_name(self, name):
        return self.model.query.filter_by(name=name).first()
