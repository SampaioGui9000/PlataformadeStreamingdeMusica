from pydantic import BaseModel, ConfigDict, Field


class SongBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    artist: str = Field(min_length=1, max_length=200)
    album: str | None = None
    genre: str | None = None
    duration_seconds: int = Field(gt=0)


class SongCreate(SongBase):
    pass


class SongUpdate(BaseModel):
    title: str | None = None
    artist: str | None = None
    album: str | None = None
    genre: str | None = None
    duration_seconds: int | None = Field(default=None, gt=0)


class SongOut(SongBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class PlaylistBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None


class PlaylistCreate(PlaylistBase):
    pass


class PlaylistUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class PlaylistOut(PlaylistBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    songs: list[SongOut] = []
