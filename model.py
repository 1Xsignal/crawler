from sqlalchemy import create_engine, Column, String, Integer, BigInteger, Text, ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import insert as ins
from datetime import datetime

Base = declarative_base()

# اتصال به پایگاه داده
DATABASE_URL = 'postgresql://postgres:sajadsajad@localhost:5432/currency'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# مدل جدول Currency
class Currency(Base):
    __tablename__ = 'currency'
    title = Column(String(100), primary_key=True)
    date_and_time = Column(TIMESTAMP, nullable=False)


    @classmethod
    def insert(cls, title, date_and_time=None):
        """متد درج اطلاعات در جدول Currency با ON CONFLICT"""
        try:
            if date_and_time is None:
                date_and_time = datetime.now()

            # تنظیم INSERT با ON CONFLICT
            stmt = ins(cls).values(
                title=title,
                date_and_time=date_and_time
            ).on_conflict_do_nothing(index_elements=['title'])  # ستون اصلی برای بررسی تکرار

            # اجرای کوئری
            session.execute(stmt)
            session.commit()
            print(f"Currency '{title}' inserted (if not exists).")
        except Exception as e:
            session.rollback()
            print(f"Error inserting Currency '{title}': {e}")


# مدل جدول ChannelOfTelegram
class ChannelOfTelegram(Base):
    __tablename__ = 'channel_of_telegram'
    telegram_unique_id = Column(BigInteger, primary_key=True)
    user_name = Column(String(100), nullable=True)
    logo= Column(String(255), nullable=True)
    signalTerm= Column(String(255), nullable=True)
    trading_market= Column(String(255), nullable=True)

    @classmethod
    def insert(cls, telegram_unique_id, user_name=None,logo=None,signalTerm=None,trading_market=None):
        """متد درج اطلاعات در جدول ChannelOfTelegram با مدیریت خطا"""
        try:
            new_channel = cls(telegram_unique_id=telegram_unique_id, user_name=user_name,logo=logo,signalTerm=signalTerm,trading_market=trading_market)
            session.add(new_channel)
            session.commit()
            print(f"Channel '{telegram_unique_id}' inserted successfully!")
            return new_channel
        except Exception as e:
            session.rollback()
            print(f"Error inserting Channel '{telegram_unique_id}': {e}")
            return None

# مدل جدول SignalTable
class SignalTable(Base):
    __tablename__ = 'signal_table'
    signal_id = Column(Integer, primary_key=True, autoincrement=True)
    cur_title = Column(String(100), ForeignKey('currency.title'), nullable=False)
    channel_id = Column(BigInteger, ForeignKey('channel_of_telegram.telegram_unique_id'), nullable=False)
    entry_zone = Column(Text, nullable=True)
    leverage = Column(String(100), nullable=True)
    targets = Column(Text, nullable=True)
    short_or_long = Column(String(50), nullable=True)
    stoploss = Column(DECIMAL(10, 5), nullable=True)
    profit = Column(DECIMAL(10, 5), nullable=True)
    created_date = Column(TIMESTAMP, nullable=False)
    period_time = Column(String(50), nullable=True)

    currency = relationship('Currency', backref='signals')
    channel = relationship('ChannelOfTelegram', backref='signals')

    @classmethod
    def insert(cls, cur_title, channel_id, entry_zone, leverage, targets=None, short_or_long=None, stoploss=None,
               profit=None, created_date=None, period_time=None):
        """متد درج اطلاعات در جدول SignalTable با مدیریت خطا"""
        try:
            if created_date is None:
                created_date = datetime.now()
            new_signal = cls(
                cur_title=cur_title,
                channel_id=channel_id,
                entry_zone=entry_zone,
                leverage=leverage,
                targets=targets,
                short_or_long=short_or_long,
                stoploss=stoploss,
                profit=profit,
                created_date=created_date,
                period_time=period_time
            )
            session.add(new_signal)
            session.commit()
            print(f"Signal '{cur_title}' inserted successfully!")
            return new_signal
        except Exception as e:
            session.rollback()
            print(f"Error inserting Signal '{cur_title}': {e}")
            return None

# ایجاد جداول در پایگاه داده
if __name__ == "__main__":
    Base.metadata.create_all(engine)
