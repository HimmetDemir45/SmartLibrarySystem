from library.repositories.category_repository import CategoryRepository
from library.models.category import Category 

class CategoryService:
    category_repo = CategoryRepository()

    @staticmethod
    def get_all_categories():
        return CategoryService.category_repo.get_all()

    @staticmethod
    def get_category_by_id(category_id):
        return CategoryService.category_repo.get_by_id(category_id)

    @staticmethod
    def add_category(name):
        new_category = Category(name=name)
        return CategoryService.category_repo.add(new_category)

    @staticmethod
    def update_category(category_id, new_name):
        category = CategoryService.category_repo.get_by_id(category_id)
        if category:
            category.name = new_name
            return CategoryService.category_repo.update()
        return None

    @staticmethod
    def delete_category(category_id):
        # NOT: Silmeden önce bu kategorinin kitaba bağlı olup olmadığını kontrol etmeniz gerekebilir.
        return CategoryService.category_repo.delete(category_id)