import psycopg2

class DatabaseManager:
    _DATABASE_CONFIG = {
        "dbname": "currency",
        "user": "postgres",
        "password": "sajadsajad",
        "host": "localhost",
        "port": 5432
    }

    _CREATE_TABLE_SCRIPTS="""

CREATE TABLE IF NOT EXISTS currency1 (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    rate DECIMAL(10, 2) NOT NULL,
    date_and_time TIMESTAMP NOT NULL
);


CREATE TABLE IF NOT EXISTS currency2 (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    rate DECIMAL(10, 2) NOT NULL,
    date_and_time TIMESTAMP NOT NULL
);


CREATE TABLE IF NOT EXISTS channel_of_telegram (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_name VARCHAR(50),
    telegram_unique_id BIGINT NOT NULL
);


CREATE TABLE IF NOT EXISTS Signal_Table (
    signal_id SERIAL PRIMARY KEY,
    cur1_id INT NOT NULL,
    cur2_id INT NOT NULL,
    channel_id INT NOT NULL,
    ENTRY_ZONE VARCHAR(50),
    leverage DECIMAL(5, 2),
    targets TEXT,
    short_or_long BOOLEAN,
    stoploss DECIMAL(10, 2),
    created_date TIMESTAMP NOT NULL,
    expire_date TIMESTAMP,
    CONSTRAINT fk_cur1 FOREIGN KEY (cur1_id) REFERENCES currency1 (id),
    CONSTRAINT fk_cur2 FOREIGN KEY (cur2_id) REFERENCES currency2 (id),
    CONSTRAINT fk_channel FOREIGN KEY (channel_id) REFERENCES channel_of_telegram (id)
);
"""

    def __init__(self):
        self.connection=None
        try:
            self.connection = psycopg2.connect(**self._DATABASE_CONFIG)
            print("successfully connected to database")
            cursor=self.connection.cursor()
            cursor.execute(self._CREATE_TABLE_SCRIPTS)
            self.connection.commit()
            print('Table is created')

        except psycopg2.Error as e:
            print(f" your not succefully to connect db =  {e}")
            self.connection = None

    def close_connection(self):
        if self.connection:
            self.connection.close()
            print("connection closed")





p=DatabaseManager()
