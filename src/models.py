from typing import Any, Dict

from sqlalchemy.ext.associationproxy import association_proxy

from .app import db


def my_strtobool(val: str) -> bool:
    """Преобразует строку в булевое значение"""

    val = val.lower()

    true_values = {"1", "yes", "y", "true", "t", "on"}
    false_values = {"0", "no", "n", "false", "f", "off"}

    if val in true_values:
        return True
    elif val in false_values:
        return False
    else:
        raise ValueError(f"Недопустимое значение '{val}'.")


class Client(db.Model):  # type: ignore[name-defined]
    __tablename__ = "client"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    credit_card = db.Column(db.String(50))
    car_number = db.Column(db.String(10))

    client_parkings = db.relationship("ClientParking", back_populates="driver")
    parkings = association_proxy("client_parkings", "parking_place")

    def __repr__(self):
        return f"Клиент {self.name + ' ' + self.surname}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Parking(db.Model):  # type: ignore[name-defined]
    __tablename__ = "parking"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    opened = db.Column(db.Boolean, default=True, nullable=False)
    count_places = db.Column(db.Integer, nullable=False)
    count_available_places = db.Column(db.Integer, nullable=False)

    clients = db.relationship("ClientParking", back_populates="parking_place")
    park_clients = association_proxy("clients", "driver")

    def __repr__(self):
        part_one = "Парковка № {id}\nАдрес: {address}\nВсего парковочных "
        part_two = "мест: {total_places}\nСвободно парковочных "
        part_three = "мест: {free_places}\nПарковка: {status}"
        phrase = part_one + part_two + part_three
        return phrase.format(
            id=self.id,
            address=self.address,
            total_places=self.count_places,
            free_places=self.count_available_places,
            status="ОТКРЫТА" if self.opened else "ЗАКРЫТА",
        )

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class ClientParking(db.Model):  # type: ignore[name-defined]
    __tablename__ = "client_parking"

    id = db.Column(db.Integer, primary_key=True)
    time_in = db.Column(db.DateTime)
    time_out = db.Column(db.DateTime)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    parking_id = db.Column(db.Integer, db.ForeignKey("parking.id"))

    __table_args__ = (db.UniqueConstraint("client_id", "parking_id", name="ucp"),)

    driver = db.relationship("Client", back_populates="client_parkings")
    parking_place = db.relationship("Parking", back_populates="clients")

    def __repr__(self):
        a = self.driver
        b = self.parking_id
        c = self.time_in
        return f"{a} заехал на парковку № {b} {c}."
