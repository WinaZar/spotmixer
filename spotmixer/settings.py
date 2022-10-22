import pathlib

from pydantic import BaseSettings


class Settings(BaseSettings):
    spotipy_client_id: str
    spotipy_client_secret: str
    spotify_user_name: str
    spotify_token_scope: str = 'playlist-modify-private'
    project_root: pathlib.Path = pathlib.Path(__file__).parent.parent


def get_settings() -> Settings:
    return Settings()
