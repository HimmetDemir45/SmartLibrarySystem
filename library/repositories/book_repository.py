from library.repositories.base_repository import BaseRepository
from library.models.book import Book
from library.models.author import Author
from library.models.category import Category
from sqlalchemy import or_

class BookRepository(BaseRepository):
    def __init__(self):
        super().__init__(Book)

    # YENİ METOD: Sayfalı listeleme
    def get_all_paginated(self, page, per_page=12):
        return self.model.query.paginate(page=page, per_page=per_page)

    # GÜNCELLENEN METOD: Arama sonuçlarını da sayfalı getiriyoruz
    def search(self, query, page, per_page=12):
        """Kitap adı, yazar, kategori veya barkoda göre arama yapar"""
        if not query:
            return self.get_all_paginated(page, per_page)

        return self.model.query.join(Author).join(Category).filter(
            or_(
                self.model.name.contains(query),
                Author.name.contains(query),
                Category.name.contains(query),
                self.model.barcode.contains(query)
            )
        ).paginate(page=page, per_page=per_page) # .all() yerine .paginate() kullandık

    def find_by_name(self, name):
        return self.model.query.filter_by(name=name).first()