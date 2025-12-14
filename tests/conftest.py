import pytest
from src.app.py import create_app, db as _db
from src.models import Client, ClientParking, Parking
from datetime import datetime


@pytest.fixture
def app():
    """ Фикстура приложения """

    _app = create_app()
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

    with _app.app_context():

        _db.create_all()
        client = Client(id=1,
                    name="Ivan",
                    surname="Ivanov",
                    credit_card='0000 1111 2222 3333',
                    car_number='A333AA')
        parking = Parking(id=1,
                          address="Stroitelei street, 25",
                          opened=True,
                          count_places=50,
                          count_available_places=25)
        client_parking = ClientParking(id=1,
                                       time_in=datetime(2025, 12, 10, 13, 48, 20, 196756),
                                       time_out=datetime(2025, 12, 10, 15, 36, 12, 383591),
                                       client_id=2,
                                       parking_id=2)
        _db.session.add(client)
        _db.session.add(parking)
        _db.session.add(client_parking)
        _db.session.commit()

        yield _app

        _db.session.close()
        _db.drop_all()


@pytest.fixture
def client(app):

    """ Фикстура клиента """

    client = app.test_client()
    yield client


@pytest.fixture
def db(app):

    """ Фикстура для связи с БД """

    with app.app_context():
        yield _db
