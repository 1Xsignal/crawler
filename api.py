from fastapi import FastAPI, Depends,Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, sessionmaker,joinedload
from sqlalchemy import create_engine, asc, desc
from typing import List, Optional
from pydantic import BaseModel,Field
from datetime import datetime
from model import Currency as CurrencyModel, ChannelOfTelegram as ChannelOfTelegramModel, \
    SignalTable as SignalTableModel, Base


DATABASE_URL = 'postgresql://postgres:sajadsajad@localhost:5432/currency'
engine = create_engine(DATABASE_URL, echo=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)

app = FastAPI()

BASE_URL = "http://localhost:8000/"
app.mount("/media", StaticFiles(directory="media"), name="media")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



class Currency(BaseModel):
    title: str
    date_and_time: datetime

    class Config:
        orm_mode = True


class ChannelOfTelegram(BaseModel):
    telegram_unique_id: int
    user_name: Optional[str] = None
    logo: Optional[str] = None
    signalTerm: Optional[str] = None
    trading_market: Optional[str] = None




class SignalTable(BaseModel):
    signal_id: int
    cur_title: str
    channel_name: Optional[str] = None
    entry_zone: Optional[str] = None
    leverage: Optional[str] = None
    targets: Optional[str] = None
    short_or_long: Optional[str] = None
    stoploss: Optional[float] = None
    profit: Optional[float] = None
    created_date: datetime
    period_time: Optional[str] = None

    class Config:
        orm_mode = True



@app.get("/currencies/", response_model=List[Currency])
async def read_currencies(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = db.query(CurrencyModel).offset(skip).limit(limit).all()
    return items


@app.get("/channels/", response_model=List[ChannelOfTelegram])
async def read_channels(request: Request, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """دریافت لیست کانال‌ها"""
    items = db.query(ChannelOfTelegramModel).offset(skip).limit(limit).all()

    # تولید URL کامل برای فایل‌های لوگو
    result = []
    for item in items:
        result.append({
            "telegram_unique_id": item.telegram_unique_id,
            "user_name": item.user_name,
            "logo": f"{request.base_url}{item.logo}" if item.logo else None,
            "signalTerm": item.signalTerm,
            "trading_market": item.trading_market
        })

    return result

    return result


@app.get("/signals/", response_model=List[SignalTable])
async def read_signals(
        skip: int = 0,
        limit: int = 10,
        cur_title: Optional[str] = None,
        channel_name: Optional[str] = None,
        sort_by: Optional[str] = "created_date",
        order: Optional[str] = "asc",
        db: Session = Depends(get_db)
):
    query = db.query(SignalTableModel).join(ChannelOfTelegramModel).options(joinedload(SignalTableModel.channel))


    if channel_name:
        query = query.filter(ChannelOfTelegramModel.user_name.ilike(f"%{channel_name}%"))


    if cur_title:
        query = query.filter(SignalTableModel.cur_title.ilike(f"%{cur_title}%"))


    if order == "desc":
        query = query.order_by(desc(getattr(SignalTableModel, sort_by, "created_date")))
    else:
        query = query.order_by(asc(getattr(SignalTableModel, sort_by, "created_date")))

    items = query.offset(skip).limit(limit).all()


    result = []
    for item in items:
        result.append({
            "signal_id": item.signal_id,
            "cur_title": item.cur_title,
            "channel_name": item.channel.user_name,
            "entry_zone": item.entry_zone,
            "leverage": item.leverage,
            "targets": item.targets,
            "short_or_long": item.short_or_long,
            "stoploss": item.stoploss,
            "profit": item.profit,
            "created_date": item.created_date,
            "period_time": item.period_time
        })

    return result
