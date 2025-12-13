import pytest
from module_29_testing.hw.flask_app.main.models import Parking, ClientParking


@pytest.mark.parametrize("route", ["/", "/clients",
                                   "/clients/1"])
def test_route_status(client, route):

    """ Проверяет, что все GET-методы возвращают код 200 """

    rv = client.get(route)
    assert rv.status_code == 200


def test_create_client(client) -> None:
    """ Тестирование создания клиента """

    client_data = {"name": "Natalia", "surname": "Vorontsova",
                 "credit_card": "4567 1928 2222 0004",
                   "car_number": "L476NR"}
    resp = client.post("/clients", data=client_data)
    assert resp.status_code == 201


def test_create_parking(client) -> None:
    """ Тестирование создания парковки """

    parking_data = {"address": "Tverskaya street, 23", "opened": True,
                 "count_places": 200,
                   "count_available_places": 56}
    resp = client.post("/parkings", data=parking_data)
    assert resp.status_code == 201


@pytest.mark.parking
def test_parking_entry(client, db) -> None:
    """ Тестирование заезда на парковку:
        - количество свободных мест на парковке уменьшается на 1
        - открыта ли парковка
        - у клиента привязана карта
        - POST-метод возвращает код 201
    """

    entry_parking_data = {"client_id": 1,
                           "parking_id": 1}

    parking = db.session.query(Parking).get(entry_parking_data['parking_id'])
    parking_capacity_before_request = parking.count_available_places
    resp = client.post("/client_parkings", data=entry_parking_data)
    data = resp.data.decode()
    parking_capacity_after_request = parking.count_available_places

    assert parking_capacity_before_request - parking_capacity_after_request == 1
    assert data != "Parking is closed"
    assert data != 'There is no credit card assigned to client'
    assert resp.status_code == 201


@pytest.mark.parking
def test_parking_exit(client, db) -> None:
    """ Тестирование выезда с парковки:
        - время выезда не может быть меньше времени заезда
        - количество свободных мест на парковке увеличивается на 1
        - POST-метод возвращает код 201
    """

    exit_parking_data = {"client_id": 1,
                           "parking_id": 1}

    resp_1 = client.post("/client_parkings", data=exit_parking_data)
    parking = db.session.query(Parking).get(exit_parking_data['parking_id'])
    parking_capacity_before_request = parking.count_available_places
    resp_2 = client.delete("/client_parkings", data=exit_parking_data)
    parking_capacity_after_request = parking.count_available_places
    client_parking = db.session.query(ClientParking).get(1)

    assert client_parking.time_out > client_parking.time_in
    assert parking_capacity_after_request - parking_capacity_before_request == 1
    assert resp_2.status_code == 200
