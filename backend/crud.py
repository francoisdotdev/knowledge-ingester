from sqlmodel import Session, select
import models
from sqlalchemy import exc

def create_link(session: Session, link: models.Link) -> models.Link:
    try:
        db_link = link
        session.add(db_link)
        session.commit()
        session.refresh(db_link)
        return db_link
    except exc.OperationalError as e:
        session.rollback()
        print(f"Database connection error: {e}")
        raise
    except Exception as e:
        session.rollback()
        print(f"Error creating link: {e}")
        raise


def get_links(session: Session, skip: int = 0, limit: int = 100) -> list[models.Link]:
    return session.exec(select(models.Link).offset(skip).limit(limit)).all()


def get_link_by_id(session: Session, link_id: int) -> models.Link | None:
    return session.get(models.Link, link_id)


def delete_link(session: Session, link_id: int) -> bool:
    link = session.get(models.Link, link_id)
    if link:
        session.delete(link)
        session.commit()
        return True
    return False
