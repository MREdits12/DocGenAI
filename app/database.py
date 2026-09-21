"""DocGen AI - Database setup"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import get_settings

db_url = get_settings().database_url
connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency for getting a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    
    # Auto-migrate Postgres Enums to support new AI tools
    if str(engine.url).startswith("postgresql"):
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT")
            new_tools = ["social_media", "email", "blog", "product_desc", "youtube", "ad_copy", "rewrite"]
            for tool in new_tools:
                try:
                    conn.execute(text(f"ALTER TYPE documenttype ADD VALUE '{tool}'"))
                except Exception:
                    pass
