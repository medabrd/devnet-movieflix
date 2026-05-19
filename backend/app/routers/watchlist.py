from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, WatchlistItem
from app.schemas import WatchlistAdd, WatchlistItemOut
from app.security import get_current_user

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


@router.get("", response_model=list[WatchlistItemOut])
def list_items(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == user.id)
        .order_by(WatchlistItem.added_at.desc())
        .all()
    )


@router.post("", response_model=WatchlistItemOut, status_code=201)
def add_item(
    payload: WatchlistAdd,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = WatchlistItem(
        user_id=user.id,
        tmdb_id=payload.tmdb_id,
        title=payload.title,
        poster_path=payload.poster_path,
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Already in watchlist")
    db.refresh(item)
    return item


@router.delete("/{tmdb_id}", status_code=204)
def remove_item(
    tmdb_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == user.id, WatchlistItem.tmdb_id == tmdb_id)
        .first()
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
