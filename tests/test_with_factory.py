from .factories import ClientFactory, ParkingFactory
from ..src.models import Client, Parking


def test_create_client(app, db):
    """ Тестирование создания клиента, используя ClientFactory """

    fake_client = ClientFactory()
    db.session.commit()
    print('\n' + repr(fake_client))

    assert fake_client.id is not None
    assert len(db.session.query(Client).all()) == 2


def test_create_parking(client, db):
    """ Тестирование создания парковки, используя ParkingFactory """

    fake_parking = ParkingFactory()
    db.session.commit()
    print('\n' + repr(fake_parking))

    assert fake_parking.id is not None
    assert len(db.session.query(Parking).all()) == 2
