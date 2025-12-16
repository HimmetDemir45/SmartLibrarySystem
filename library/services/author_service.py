from library.repositories.author_repository import AuthorRepository
from library.models.author import Author

class AuthorService:
    author_repo = AuthorRepository()

    @staticmethod
    def get_all_authors():
        return AuthorService.author_repo.get_all()

    @staticmethod
    def get_author_by_id(author_id):
        return AuthorService.author_repo.get_by_id(author_id)

    @staticmethod
    def add_author(name):
        new_author = Author(name=name)
        return AuthorService.author_repo.add(new_author)

    @staticmethod
    def update_author(author_id, new_name):
        author = AuthorService.author_repo.get_by_id(author_id)
        if author:
            author.name = new_name
            return AuthorService.author_repo.update() # update() muhtemelen commit yapar
        return None

    @staticmethod
    def delete_author(author_id):
        # NOT: Silmeden önce bu yazarın kitaba bağlı olup olmadığını kontrol etmeniz gerekebilir.
        return AuthorService.author_repo.delete(author_id)