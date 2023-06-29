import mysql.connector
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)


@dataclass
class Price:
    coin_name: str
    time_stamp: datetime
    price: float


def main() -> None:
    handle_subscriptions()
    get_data()


def get_data() -> None:
    logging.info("Trying to fetch coin names.")
    response = requests.get("http://coinnews:8000/api/data")
    response.raise_for_status()

    coins = response.json()
    logging.info('The coin names "{}" are fetched.'.format(coins))

    new_prices = []
    for coin in coins:
        logging.info('Trying to fetch current price of the "{}" coin.'.format(coin))
        response = requests.get("http://coinnews:8000/api/data/{}".format(coin))
        response.raise_for_status()
        data = response.json()
        new_price = Price(
            coin_name=data["name"],
            time_stamp=datetime.strptime(data["updated_at"][:-4], "%Y-%m-%dT%H:%M:%S.%f"),
            price=float(data["value"]),
        )
        new_prices.append(new_price)
        logging.info('The coin "{}" price data is "{}".'.format(coin, asdict(new_price)))

    connection = create_connection()    
    cursor = connection.cursor()
    for price in new_prices:
        cursor.execute(
            "INSERT INTO prices (coin_name, time_stamp, price) VALUES (%s, %s, %s)",
            (price.coin_name, price.time_stamp.strftime("%Y-%m-%d %H:%M:%S"), price.price)
        )

    logging.info("Trying to update the database.")
    connection.commit()
    logging.info("The database is updated.")
    
    connection.close()


def handle_subscriptions() -> None:

    coin_dict = {}

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT coin_name FROM prices")
    rows = cursor.fetchall()

    for row in rows:
        cursor.execute("SELECT * FROM prices where coin_name = " + str(row))
        results = cursor.fetchall()
        new_value = float(results[-1][2])
        old_value = float(result[-2][2])
        coin_dict[row] = int( ( (new_value - old_value) / old_value) * 100)

    #get alert subsccriptions
    cursor.execute("SELECT * FROM alert_subscriptions")
    rows = cursor.fetchall()

    #check if should send email to user
    for row in rows:
        if row[1] in coin_dict:
            if coin_dict[row[1]] >= int(row[2]):
                send_email(str(row[0]), str(row[1]))

    
    connection.close()


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


def send_email(toAddress, cName):
    message = MIMEMultipart()
    message["To"] = toAddress
    message["From"] = 'eer6947@gmail.com'
    message["Subject"] = 'Coin price Alert!'

    title = '<b>' + cName + ' price changes alert! <b>'
    messageText = MIMEText("Dear sir! <br>Your alert for the " + cName + " price changes has been activated! <br><br>Thanks for using our service. <br>Feel free to add more alerts for other coins." ,'html')
    message.attach(messageText)

    email = 'eer6947@gmail.com'
    password = 'ixxkgdfyadcmquij'

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo('Gmail')
    server.starttls()
    server.login(email,password)
    fromaddr = 'eer6947@gmail.com'
    toaddrs  = toAddress
    server.sendmail(fromaddr,toaddrs,message.as_string())

    server.quit()


if __name__ == "__main__":
    main()
