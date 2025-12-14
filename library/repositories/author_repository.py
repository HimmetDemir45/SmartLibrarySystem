from library.repositories.base_repository import BaseRepository
from library.models.author import Author

class AuthorRepository(BaseRepository):
    def __init__(self):
        super().__init__(Author)

    def get_by_name(self, name):
        return self.model.query.filter_by(name=name).first()    