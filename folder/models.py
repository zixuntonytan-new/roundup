from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    Boolean, DateTime, Date, ForeignKey, Text
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./macro.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class SeriesMeta(Base):
    __tablename__ = "series_meta"

    id        = Column(Integer, primary_key=True)
    series_id = Column(String, unique=True, nullable=False)
    title     = Column(String)
    units     = Column(String)
    frequency = Column(String)
    source    = Column(String)        # "fred", "bls", "haver"
    desk      = Column(String, default="markets")  # "markets", "macro", "news", "calendar"
    pinned    = Column(Boolean, default=False)

    observations = relationship("SeriesData", back_populates="meta")


class SeriesData(Base):
    __tablename__ = "series_data"

    id         = Column(Integer, primary_key=True)
    series_id  = Column(String, ForeignKey("series_meta.series_id"), nullable=False)
    obs_date   = Column(Date, nullable=False)
    value      = Column(Float)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    meta = relationship("SeriesMeta", back_populates="observations")


class Headline(Base):
    __tablename__ = "headlines"

    id           = Column(Integer, primary_key=True)
    source       = Column(String)
    desk         = Column(String, default="news")  # "news", "markets", "macro", etc.
    title        = Column(Text, nullable=False)
    url          = Column(String, unique=True, nullable=False)
    summary      = Column(Text)
    published_at = Column(DateTime)
    importance   = Column(Integer, default=1)
    flagged      = Column(Boolean, default=False)
    fetched_at   = Column(DateTime, default=datetime.utcnow)

    tags = relationship("Tag", secondary="headline_tags", back_populates="headlines")


class Tag(Base):
    __tablename__ = "tags"

    id    = Column(Integer, primary_key=True)
    name  = Column(String, unique=True, nullable=False)
    color = Column(String, default="#888888")

    headlines = relationship("Headline", secondary="headline_tags", back_populates="tags")


class HeadlineTag(Base):
    __tablename__ = "headline_tags"

    headline_id = Column(Integer, ForeignKey("headlines.id"), primary_key=True)
    tag_id      = Column(Integer, ForeignKey("tags.id"), primary_key=True)


class CalendarEvent(Base):  # type: ignore[name-defined]  # Base comes from app/models.py
    """
    Upcoming and past economic calendar events.

    Populated by collectors/calendar_bea.py (and future collectors for
    BLS, FOMC, Fed releases, etc.).
    """

    __tablename__ = "calendar_events"

    id            = Column(Integer, primary_key=True, index=True)

    # --- identity ---
    source        = Column(String, nullable=False, default="bea")
    # e.g. 'national_accounts', 'trade', 'regional', 'fomc', 'bls'
    category      = Column(String, nullable=False, default="")
    title         = Column(String, nullable=False)
    period        = Column(String, nullable=True)   # "Q1 2026", "Mar 2026"
    release_type  = Column(String, nullable=True)   # 'advance','second','third','annual',''
    url           = Column(String, nullable=True)

    # --- timing ---
    event_time    = Column(DateTime(timezone=True), nullable=True)
    fetched_at    = Column(DateTime(timezone=True),
                           default=lambda: datetime.now(tz=timezone.utc))

    # --- data values ---
    actual        = Column(Float,  nullable=True)
    prior         = Column(Float,  nullable=True)
    prior_period  = Column(String, nullable=True)   # "Q4 2025", "Feb 2026"
    forecast      = Column(Float,  nullable=True)   # consensus; filled manually or future scraper
    forecast_source = Column(String, nullable=True) # 'manual', 'trading_economics', etc.
    unit          = Column(String, nullable=True)   # '% annualized', '% m/m', '$B'

    # --- display controls ---
    importance    = Column(Integer, nullable=False, default=2)  # 1=low 2=med 3=high
    enabled       = Column(Boolean, nullable=False, default=True)
    desk          = Column(String,  nullable=False, default="calendar")



def init_db():
    Base.metadata.create_all(bind=engine)
