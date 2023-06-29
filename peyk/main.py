from fastapi import FastAPI
import logging
from pydantic import BaseModel
import mysql.connector
from typing import List


api = FastAPI()


class Price(BaseModel):
    coin_name: str
    time_stamp: str
    price: float

class Item(BaseModel):
    userEmail: str
    coinName: str
    rate: str


@api.get('/price')
def get_price_history(coin: str) -> List[Price]:
    if coin:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM prices WHERE coin_name = " + coin)
        rows = cursor.fetchall()
        connection.close()
    else:
        return 'please provide a coin name!'
    if rows:
        return [
            Price(coin_name=row[0], time_stamp=str(row[1]), price=row[2])
            for row in rows
        ]
    else:
        return 'No history for this coin!'


@api.post('/subscribe')
def subscribe_coin(item: Item):
    logging.info("Trying to add new alert to the database.")
    connection = create_connection()    
    cursor = connection.cursor()
    cursor.execute(
            "INSERT INTO alert_subscriptions (email, coin_name, difference_percentage ) VALUES (%s, %s, %s)",
            (item.userEmail, item.coinName, item.rate)
    )

    logging.info("Trying to update the database.")
    connection.commit()
    logging.info("The database is updated.")
    connection.close()
    return 'New alert add to the database and you will be inform by an email whenever this change happens!'


def create_connection() -> mysql.connector.MySQLConnection:
    logging.info("Trying to connect to the database.")
    connection =  mysql.connector.connect(
        user="root",
        port=3306,
        host="database",
        database="final",
    )
    logging.info("Connected to the database.")
    return connection
