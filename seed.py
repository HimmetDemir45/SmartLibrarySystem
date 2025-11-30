from market import app, db
from market.models import Item


with app.app_context():

    item1 = Item(name="Kitap-1", price=1500, barcode="123456789012", description="A true story of love")
    item2 = Item(name="Kitap-2", price=800, barcode="987654321098", description="a")
    item3 = Item(name="Kitap-3", price=200, barcode="456789123456", description="b")
    item4 = Item(name="Kitap-4", price=100, barcode="321654987654", description="c")


    db.session.add_all([item1, item2, item3, item4])
    db.session.commit()

    print("Seed işlemi tamamlandı: Ürünler eklendi.")
