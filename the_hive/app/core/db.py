from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine, text
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

database_url = str(settings.DATABASE_URL)
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(
    database_url,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,
)


def init_db() -> None:
    from sqlmodel import SQLModel
    
    # Import all models to ensure they're registered with SQLModel
    from app.models.user import User  # noqa: F401
    from app.models.tag import Tag  # noqa: F401
    from app.models.offer import Offer  # noqa: F401
    from app.models.need import Need  # noqa: F401
    from app.models.participant import Participant  # noqa: F401
    from app.models.ledger import LedgerEntry, Transfer  # noqa: F401
    from app.models.rating import Rating  # noqa: F401
    from app.models.report import Report  # noqa: F401
    from app.models.forum import ForumTopic  # noqa: F401
    from app.models.associations import OfferTag, NeedTag  # noqa: F401
    from app.models.notification import Notification  # noqa: F401
    from app.models.semantic_tag import SemanticTagSynonym, SemanticTagProperty  # noqa: F401
    
    logger.info("Initializing database tables")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables initialized")


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


SessionDep = Annotated[Session, Depends(get_session)]


def check_db_connection() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            connection.commit()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
