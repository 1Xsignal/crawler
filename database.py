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

CREATE TABLE IF NOT EXISTS currency (
    title VARCHAR(100) PRIMARY KEY,
    date_and_time TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS channel_of_telegram (
    telegram_unique_id BIGINT PRIMARY KEY,
    user_name VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS Signal_Table (
    signal_id SERIAL PRIMARY KEY,
    cur_title VARCHAR(100) NOT NULL,
    channel_id BIGINT NOT NULL, 
    ENTRY_ZONE VARCHAR(50) NOT NULL, 
    leverage DECIMAL(10, 5) NOT NULL, 
    targets TEXT,
    short_or_long VARCHAR(50),
    stoploss DECIMAL(10, 5),
    profit decimal(10,5) ,
    created_date TIMESTAMP NOT NULL,
    period_time VARCHAR(50),
    CONSTRAINT fk_cur FOREIGN KEY (cur_title) REFERENCES currency (title),
    CONSTRAINT fk_channel FOREIGN KEY (channel_id) REFERENCES channel_of_telegram (telegram_unique_id)
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


    def insert_channel(self, telegram_unique_id, user_name):
        """Insert or update a channel in the channel_of_telegram table."""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO channel_of_telegram (telegram_unique_id, user_name)
            VALUES (%s, %s)
            ON CONFLICT (telegram_unique_id)
            DO UPDATE SET user_name = EXCLUDED.user_name;
            """
            cursor.execute(query, (telegram_unique_id, user_name))
            self.connection.commit()
            print(f"Channel with ID {telegram_unique_id} has been inserted or updated.")
        except psycopg2.Error as e:
            print(f"Failed to upsert channel: {e}")

    def insert_currency(self, title, date_and_time):
        """Insert data into the currency table."""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO currency (title, date_and_time)
            VALUES (%s, %s)
            ON CONFLICT (title) DO NOTHING;
            """
            cursor.execute(query, (title, date_and_time))
            self.connection.commit()
            print(f"Currency '{title}' inserted or skipped if exists.")
        except psycopg2.Error as e:
            print(f"Failed to insert into currency: {e}")

    def insert_signal(self, cur_title, channel_id, entry_zone, leverage, targets, short_or_long, stoploss,profit, created_date,
                      period):
        """Insert data into the Signal_Table."""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO Signal_Table (cur_title, channel_id, ENTRY_ZONE, leverage, targets, short_or_long, stoploss,profit, created_date, period_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, (
            cur_title, channel_id, entry_zone, leverage, targets, short_or_long, stoploss,profit, created_date, period))
            self.connection.commit()
            print(f"Signal for currency '{cur_title}' inserted.")
        except psycopg2.Error as e:
            print(f"Failed to insert into Signal_Table: {e}")




db=DatabaseManager()

