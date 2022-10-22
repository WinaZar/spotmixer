import itertools
import random
import typing

from spotipy.client import Spotify
from spotipy.util import prompt_for_user_token

from spotmixer.settings import get_settings

T = typing.TypeVar('T')


def batched(*, iterable: typing.Iterable[T], size: int) -> typing.Generator[list[T], None, None]:
    """
    Batch data into lists of length n. The last batch may be shorter.

    batched('ABCDEFG', 3) --> ABC DEF G
    """
    iterator = iter(iterable)
    while True:
        batch = list(itertools.islice(iterator, size))
        if not batch:
            return
        yield batch


class PlaylistRandomizer:
    def __init__(self) -> None:
        self._sys_random = random.SystemRandom()
        self.settings = get_settings()
        self._token = prompt_for_user_token(
            username=self.settings.spotify_user_name,
            scope=self.settings.spotify_token_scope,
            client_id=self.settings.spotipy_client_id,
            client_secret=self.settings.spotipy_client_secret,
            redirect_uri='https://localhost:8080/callback',
            cache_path=self.settings.project_root / '.credentials.json',
        )
        self.spotify_client = Spotify(auth=self._token)

    def _get_playlist_track_ids(self, *, playlist_id: str) -> list[int]:
        tracks_batch_size = 100
        track_ids: set[int] = set()
        total_tracks_count = self.spotify_client.user_playlist_tracks(
            user=self.settings.spotify_user_name, playlist_id=playlist_id, fields='total'
        )['total']
        offset = 0
        while total_tracks_count > len(track_ids):
            tracks = self.spotify_client.user_playlist_tracks(
                user=self.settings.spotify_user_name,
                playlist_id=playlist_id,
                fields='items(track(id))',
                limit=tracks_batch_size,
                offset=offset,
            )
            for item in tracks['items']:
                track_ids.add(item['track']['id'])
            offset += tracks_batch_size

        return list(track_ids)

    def _get_randomized_playlist_track_ids(self, *, playlist_id: str) -> list[int]:
        track_ids = self._get_playlist_track_ids(playlist_id=playlist_id)
        self._sys_random.shuffle(track_ids)
        return track_ids

    def _clear_playlist(self, *, playlist_id: str) -> None:
        track_ids = self._get_playlist_track_ids(playlist_id=playlist_id)
        self.spotify_client.user_playlist_remove_all_occurrences_of_tracks(
            user=self.settings.spotify_user_name, playlist_id=playlist_id, tracks=track_ids
        )

    def _add_tracks_to_playlist(self, playlist_id: str, track_ids: list[int]) -> None:
        for batch in batched(iterable=track_ids, size=100):
            self.spotify_client.user_playlist_add_tracks(
                user=self.settings.spotify_user_name, playlist_id=playlist_id, tracks=batch
            )

    def randomize_playlist(self, *, source_playlist_id: str, target_playlist_id: str) -> None:
        self._clear_playlist(playlist_id=target_playlist_id)
        randomized_tracks_ids = self._get_randomized_playlist_track_ids(
            playlist_id=source_playlist_id
        )
        self._add_tracks_to_playlist(
            playlist_id=target_playlist_id, track_ids=randomized_tracks_ids
        )
