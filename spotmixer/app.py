from typer import Option, Typer, echo

from spotmixer.randomizer import PlaylistRandomizer

app = Typer()


@app.command()
def ping() -> None:
    echo('pong')


@app.command()
def randomize_playlist(
    source_id: str = Option(..., help='Source playlist id'),
    target_id: str = Option(..., help='Target playlist id'),
) -> None:
    echo('Randomizing started')
    randomizer = PlaylistRandomizer()
    randomizer.randomize_playlist(source_playlist_id=source_id, target_playlist_id=target_id)
    echo('Randomizing completed')
