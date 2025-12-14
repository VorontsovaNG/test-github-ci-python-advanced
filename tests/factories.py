import factory
from factory import Faker
from ..src.app import db
from ..src.models import Parking, Client


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session

    name = Faker('first_name', locale='ru_RU')
    surname = Faker('last_name', locale='ru_RU')
    credit_card = Faker('credit_card_number')
    car_number = Faker('license_plate', locale='ru_RU')


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session

    address = Faker('address', locale='ru_RU')
    opened = Faker('boolean')
    count_places = Faker('random_int', min=50, max=300, step=1)
    count_available_places = Faker('random_int', min=5, max=count_places, step=1)
