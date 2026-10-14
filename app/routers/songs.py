from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/songs", tags=["songs"])


@router.post("", response_model=schemas.SongOut, status_code=status.HTTP_201_CREATED)
def create_song(payload: schemas.SongCreate, db: Session = Depends(get_db)):
    song = models.Song(**payload.model_dump())
    db.add(song)
    db.commit()
    db.refresh(song)
    return song


@router.get("", response_model=list[schemas.SongOut])
def list_songs(
    artist: str | None = None,
    genre: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(models.Song)
    if artist:
        stmt = stmt.where(models.Song.artist.ilike(f"%{artist}%"))
    if genre:
        stmt = stmt.where(models.Song.genre == genre)
    return db.scalars(stmt.order_by(models.Song.id).offset(skip).limit(limit)).all()


@router.get("/{song_id}", response_model=schemas.SongOut)
def get_song(song_id: int, db: Session = Depends(get_db)):
    song = db.get(models.Song, song_id)
    if not song:
        raise HTTPException(404, "Música não encontrada")
    return song


@router.put("/{song_id}", response_model=schemas.SongOut)
def update_song(song_id: int, payload: schemas.SongUpdate, db: Session = Depends(get_db)):
    song = db.get(models.Song, song_id)
    if not song:
        raise HTTPException(404, "Música não encontrada")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(song, key, value)
    db.commit()
    db.refresh(song)
    return song


@router.delete("/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_song(song_id: int, db: Session = Depends(get_db)):
    song = db.get(models.Song, song_id)
    if not song:
        raise HTTPException(404, "Música não encontrada")
    db.delete(song)
    db.commit()
