CREATE DATABASE final;

USE final;

CREATE TABLE prices (
    coin_name VARCHAR(255),
    time_stamp TIMESTAMP,
    price FLOAT,
    PRIMARY KEY (coin_name, time_stamp)
);

CREATE TABLE alert_subscriptions (
    email VARCHAR(255),
    coin_name VARCHAR(255),
    difference_percentage INT,
    PRIMARY KEY (email, coin_name, difference_percentage)
);
