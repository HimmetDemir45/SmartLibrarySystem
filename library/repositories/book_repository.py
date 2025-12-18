from library.models.book import Book
from library.repositories.base_repository import BaseRepository
from sqlalchemy.orm import joinedload

class BookRepository(BaseRepository):
    def __init__(self):
        super().__init__(Book)

    def search(self, query, page=1, per_page=12):
        # Arama işlemi - yazar ve kategori adına göre de arama yapılabilir
        # Eager loading ile author ve category ilişkilerini yüklüyoruz
        from library.models.author import Author
        from library.models.category import Category
        
        books = Book.query.options(
            joinedload(Book.author),
            joinedload(Book.category)
        )
        if query:
            # Yazar ve kategoriye göre arama için outer join kullanıyoruz
            books = books.outerjoin(Author).outerjoin(Category).filter(
                (Book.name.ilike(f'%{query}%')) |
                (Book.barcode.ilike(f'%{query}%')) |
                (Book.description.ilike(f'%{query}%')) |
                (Author.name.ilike(f'%{query}%')) |
                (Category.name.ilike(f'%{query}%'))
            ).distinct()
        return books.paginate(page=page, per_page=per_page)

    def find_by_name(self, name):
        return Book.query.options(
            joinedload(Book.author),
            joinedload(Book.category)
        ).filter_by(name=name).first()

    def get_all_paginated(self, page=1, per_page=12):
        return Book.query.options(
            joinedload(Book.author),
            joinedload(Book.category)
        ).paginate(page=page, per_page=per_page)

    # --- YENİ EKLENEN KİLİTLİ SORGULAMA METODU ---
    def get_by_id_with_lock(self, id):
        """
        Kitabı ID'ye göre getirir ve işlem (transaction) bitene kadar
        bu satırı veritabanında kilitler (SELECT ... FOR UPDATE).
        """
        return Book.query.options(
            joinedload(Book.author),
            joinedload(Book.category)
        ).filter_by(id=id).with_for_update().first()

    def find_by_barcode(self, barcode):
        """Barkoda göre tekil kitap döndürür."""
        return Book.query.options(
            joinedload(Book.author),
            joinedload(Book.category)
        ).filter_by(barcode=barcode).first()