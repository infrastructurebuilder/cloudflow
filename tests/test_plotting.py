"""cloudflow.plotting works out file names and map tiles as it did as its own distribution."""

from __future__ import annotations

import pytest

from cloudflow.plotting import shared, tile


def test_plot_name_for_nos_output() -> None:
    name = shared.set_filename(
        "/com/nos/cbofs.20200309/nos.cbofs.fields.f001.20200309.t00z.nc", "temp", "/out"
    )
    assert name == "/out/f001_temp.png"


def test_plot_name_for_roms_history_output() -> None:
    name = shared.set_filename("/com/liveocean/current/ocean_his_0001.nc", "salt", "/out")
    assert name == "/out/f001_salt.png"


def test_difference_plot_name() -> None:
    name = shared.set_diff_filename("/com/nos/nos.cbofs.fields.f012.20200309.t00z.nc", "zeta", "/out")
    assert name == "/out/f012_zeta_diff.png"


def test_tile_for_a_longitude_and_latitude() -> None:
    grid = tile.Tile4326()
    assert grid.tile(-76.0, 38.0, 5) == (9, 12, 5)
    assert grid.bounds(9, 12, 5) == (-78.75, 33.75, -67.5, 45.0)


@pytest.mark.parametrize("zoom", [0, 1, 4, 9])
@pytest.mark.parametrize(("lon", "lat"), [(-76.0, 38.0), (-122.4, 47.6), (0.5, -0.5), (151.2, -33.9)])
def test_a_tile_contains_the_point_it_was_computed_for(lon: float, lat: float, zoom: int) -> None:
    grid = tile.Tile4326()
    x, y, z = grid.tile(lon, lat, zoom)
    west, south, east, north = grid.bounds(x, y, z)
    assert west <= lon <= east
    assert south <= lat <= north
