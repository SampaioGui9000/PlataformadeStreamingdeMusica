from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/playlists", tags=["playlists"])


def _get_playlist(db: Session, playlist_id: int) -> models.Playlist:
    playlist = db.get(models.Playlist, playlist_id)
    if not playlist:
        raise HTTPException(404, "Playlist não encontrada")
    return playlist


@router.post("", response_model=schemas.PlaylistOut, status_code=status.HTTP_201_CREATED)
def create_playlist(payload: schemas.PlaylistCreate, db: Session = Depends(get_db)):
    playlist = models.Playlist(**payload.model_dump())
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return playlist


@router.get("", response_model=list[schemas.PlaylistOut])
def list_playlists(db: Session = Depends(get_db)):
    return db.scalars(select(models.Playlist).order_by(models.Playlist.id)).all()


@router.get("/{playlist_id}", response_model=schemas.PlaylistOut)
def get_playlist(playlist_id: int, db: Session = Depends(get_db)):
    return _get_playlist(db, playlist_id)


@router.put("/{playlist_id}", response_model=schemas.PlaylistOut)
def update_playlist(playlist_id: int, payload: schemas.PlaylistUpdate, db: Session = Depends(get_db)):
    playlist = _get_playlist(db, playlist_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(playlist, key, value)
    db.commit()
    db.refresh(playlist)
    return playlist


@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_playlist(playlist_id: int, db: Session = Depends(get_db)):
    db.delete(_get_playlist(db, playlist_id))
    db.commit()


@router.post("/{playlist_id}/songs/{song_id}", response_model=schemas.PlaylistOut)
def add_song(playlist_id: int, song_id: int, db: Session = Depends(get_db)):
    playlist = _get_playlist(db, playlist_id)
    song = db.get(models.Song, song_id)
    if not song:
        raise HTTPException(404, "Música não encontrada")
    if song in playlist.songs:
        raise HTTPException(409, "Música já está na playlist")
    playlist.songs.append(song)
    db.commit()
    db.refresh(playlist)
    return playlist


@router.delete("/{playlist_id}/songs/{song_id}", response_model=schemas.PlaylistOut)
def remove_song(playlist_id: int, song_id: int, db: Session = Depends(get_db)):
    playlist = _get_playlist(db, playlist_id)
    song = db.get(models.Song, song_id)
    if not song or song not in playlist.songs:
        raise HTTPException(404, "Música não está na playlist")
    playlist.songs.remove(song)
    db.commit()
    db.refresh(playlist)
    return playlist
