from library.repositories.book_repository import BookRepository
from library.repositories.author_repository import AuthorRepository
from library.repositories.category_repository import CategoryRepository
from library.models.book import Book
from library.models.author import Author
from library.models.category import Category

class BookService:
    # Depoları başlatıyoruz (Dependency Injection benzeri)
    book_repo = BookRepository()
    author_repo = AuthorRepository()
    category_repo = CategoryRepository()

    @staticmethod
    def get_all_books(page=1): # page parametresi eklendi
        return BookService.book_repo.get_all_paginated(page=page)

    @staticmethod
    def get_book_by_id(book_id):
        return BookService.book_repo.get_by_id(book_id)

    @staticmethod
    def search_books(query, page=1): # page parametresi eklendi
        return BookService.book_repo.search(query, page=page)


    @staticmethod
    def get_book_by_name(book_name):
        return BookService.book_repo.find_by_name(book_name)

    @staticmethod
    def add_book(name, author_name, category_name, barcode, description, image_file='default.jpg'):
        # 1. Yazar Var mı? Yoksa oluştur.
        author = BookService.author_repo.get_by_name(author_name)
        if not author:
            author = BookService.author_repo.add(Author(name=author_name))

        # 2. Kategori Var mı? Yoksa oluştur.
        category = BookService.category_repo.get_by_name(category_name)
        if not category:
            category = BookService.category_repo.add(Category(name=category_name))

        # 3. Kitabı Ekle (image_file eklendi)
        new_book = Book(
            name=name,
            barcode=barcode,
            description=description,
            author_id=author.id,
            category_id=category.id,
            image_file=image_file,  # <-- BURASI YENİ
            is_available=True
        )
        return BookService.book_repo.add(new_book)

    @staticmethod
    def delete_book(book_id):
        book = BookService.book_repo.get_by_id(book_id)
        if book:
            BookService.book_repo.delete(book)
            return True
        return False

    @staticmethod
    def update_book(book_id, data):
        book = BookService.book_repo.get_by_id(book_id)
        if not book:
            return None

        # Temel Bilgiler
        if 'name' in data: book.name = data['name']
        if 'barcode' in data: book.barcode = data['barcode']
        if 'description' in data: book.description = data['description']

        # İlişkisel Veriler (Yazar/Kategori)
        if 'author' in data and data['author']:
            author = BookService.author_repo.get_by_name(data['author'])
            if not author:
                author = BookService.author_repo.add(Author(name=data['author']))
            book.author_id = author.id

        if 'category' in data and data['category']:
            category = BookService.category_repo.get_by_name(data['category'])
            if not category:
                category = BookService.category_repo.add(Category(name=data['category']))
            book.category_id = category.id

        # Değişiklikleri kaydet
        BookService.book_repo.update()
        return book