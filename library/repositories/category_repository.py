from library.repositories.base_repository import BaseRepository
from library.models.category import Category

class CategoryRepository(BaseRepository):
    def __init__(self):
        super().__init__(Category)

    def get_by_name(self, name):
        return self.model.query.filter_by(name=name).first()
