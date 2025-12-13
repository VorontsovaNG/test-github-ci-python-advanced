import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from typing import List
from sqlalchemy.exc import IntegrityError
import logging


db = SQLAlchemy()


def create_app():

    """ Создание flask приложения """

    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///park.db'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    from .models import Parking, Client, ClientParking, my_strtobool

    with app.app_context():
        db.create_all()


    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()


    @app.route("/", methods=['GET'])
    def get_greeting_handler() -> str:

        """Приветственная страница"""

        return 'Сервис парковки в твоем телефоне!'


    @app.route("/clients", methods=['POST'])
    def create_client_handler():

        """ Создание нового клиента """

        name = request.form.get('name', type=str)
        surname = request.form.get('surname', type=str)
        credit_card = str(request.form.get('credit_card'))
        car_number = str(request.form.get('car_number'))

        try:
            new_client = Client(name=name,
                              surname=surname,
                              credit_card=credit_card,
                              car_number=car_number)

            db.session.add(new_client)
            db.session.commit()

            return repr(new_client), 201

        except IntegrityError as e:
            db.session.rollback()
            if "(sqlite3.IntegrityError) NOT NULL constraint failed: client.name" in str(e):
                return "Ошибка: поле 'name' не может быть пустым."
            else:
                return f"Произошла ошибка целостности базы данных: {type(e)}"

        except Exception as e:
            db.session.rollback()
            return f"Произошла непредвиденная ошибка: {e}"


    @app.route("/clients", methods=['GET'])
    def get_clients_handler():

        """ Получение всех клиентов """

        clients: List[Client] = db.session.query(Client).all()
        clients_list = [u.to_json() for u in clients]

        return jsonify(clients_list), 200


    @app.route("/clients/<int:client_id>", methods=['GET'])
    def get_client_by_id_handler(client_id: int):

        """ Получение клиента по id """

        client: Client = db.session.query(Client).get(client_id)

        if client:
            return jsonify(client.to_json()), 200
        else:
            return f'Client with id {client_id} not found', 404


    @app.route("/parkings", methods=['POST'])
    def create_parking_handler():

        """ Создание новой парковочной зоны """

        address = request.form.get('address', type=str)
        str_opened = request.form.get('opened')
        opened = my_strtobool(str_opened)
        count_places = request.form.get('count_places', type=int)
        count_available_places = request.form.get('count_available_places', type=int)

        try:
            new_parking = Parking(address=address,
                                  opened=opened,
                                  count_places=count_places,
                                  count_available_places=count_available_places)

            db.session.add(new_parking)
            db.session.commit()

            return repr(new_parking), 201

        except IntegrityError as e:
            db.session.rollback()
            if "(sqlite3.IntegrityError) NOT NULL constraint failed" in str(e):
                return ("Ошибка: обязательные поля 'address', 'count_places', "
                        "'count_available_places' не могут быть пустыми.")
            else:
                return f"Произошла ошибка целостности базы данных: {type(e)}"

        except Exception as e:
            db.session.rollback()
            return f"Произошла непредвиденная ошибка: {e}"


    @app.route("/client_parkings", methods=['POST'])
    def entry_parking_handler():

        """ Заезд на парковку """

        client_id = request.form.get('client_id', type=int)
        parking_id = request.form.get('parking_id', type=int)

        current_parking_place = db.session.query(Parking).get(parking_id)
        current_client = db.session.query(Client).get(client_id)

        if current_parking_place and current_client:
            if current_parking_place.opened and current_parking_place.count_available_places > 0:

                if current_client.credit_card == 'None':
                    return 'There is no credit card assigned to client', 400
                else:
                    try:
                        current_parking_place.count_available_places -= 1
                        new_client_parking = ClientParking(time_in=datetime.datetime.now(),
                                                           client_id=client_id,
                                                           parking_id=parking_id)

                        db.session.add(new_client_parking)
                        db.session.commit()
                    except IntegrityError as e:
                        db.session.rollback()
                        if "(sqlite3.IntegrityError) UNIQUE constraint failed" in str(e):
                            return ("Ошибка: пара 'client_id - parking_id' должна быть уникальной.")
                        else:
                            return f"Произошла ошибка целостности базы данных: {type(e)}"

                    except Exception as e:
                        db.session.rollback()
                        return f"Произошла непредвиденная ошибка: {e}"

                    return repr(new_client_parking), 201

            else:
                return 'Parking is closed', 400
        else:
            return 'No parking or client with the specified id found', 404


    @app.route("/client_parkings", methods=['DELETE'])
    def update_client_parkings_handler():

        """ Выезд с парковки """

        client_id = request.form.get('client_id', type=int)
        parking_id = request.form.get('parking_id', type=int)
        current_parking_place = db.session.query(Parking).get(parking_id)

        current_client_parking = db.session.query(ClientParking).filter((ClientParking.client_id==client_id)&(ClientParking.parking_id==parking_id)).first()
        if current_client_parking:
            current_parking_place.count_available_places += 1
            current_client_parking.time_out = datetime.datetime.now()
            db.session.commit()

            car = current_client_parking.driver.car_number
            with open('parking_history.log', 'a') as file:
                file.write(f'Парковка №{current_client_parking.parking_id}: машина {car} заехала {current_client_parking.time_in}, выехала {current_client_parking.time_out}')

            db.session.query(ClientParking).filter(
                (ClientParking.client_id == client_id) & (ClientParking.parking_id == parking_id)).delete()
            db.session.commit()

            return f'Машина {car} выехала с парковки.', 200
        else:
            return f'{current_client_parking.driver} не заезжал на парковку № {parking_id}', 404

    return app