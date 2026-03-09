import itertools
import logging
from dataclasses import dataclass
from pathlib import Path

import fastkml.geometry
import fastkml.kml
import fastkml.views
from geopy import Point
from geopy.distance import great_circle

from tempren.primitives import File, Tag


@dataclass
class Place:
    name: str
    latitude: float
    longitude: float
    radius: float | None

    @property
    def position(self) -> Point:
        return Point(self.latitude, self.longitude)

    def __str__(self):
        return f"{self.name}, {self.latitude}, {self.longitude}, {self.radius}"


class KmlPlaceNameTag(Tag):
    """Convert GPS latitude/longitude coordinates into names based on the file"""

    require_context = True

    log: logging.Logger

    # TODO: Introduce global cache for storing data between different files processing
    places: list[Place]
    default: str

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def configure(  # type: ignore[override]
        self,
        kml: str,
        use_look_at: bool = True,
        use_folders: bool = True,
        default: str = "",
        to_csv: str | None = None,
    ) -> None:
        """
        :param kml: Path to the KML file containing the places
        :param use_look_at: Use LookAt attributes (instead of Point) of the placemark when looking for best matches
        :param use_folders: Add folder itself (using its LookAt) as POI
        :param default: Default value used when there is no matching POI
        Given coordinates, select best matching (closest) placemark and return its name.
        When placemarks are grouped into folders, returned name will be prefixed with it, i.e.
           FolderName/PlacemarkName
        """

        if not Path(kml).exists():
            raise FileNotFoundError(kml)

        self.places = self._load_file(kml, use_look_at, use_folders)
        self.default = default

        if to_csv is not None:
            with open(to_csv, "w") as csv_file:
                csv_file.writelines(
                    [
                        f"{p.latitude}, {p.longitude}, {p.radius / 1000 if p.radius else 0}, {p.name}\n"
                        for p in self.places
                    ]
                )

    def _load_file(
        self, kml_path: str, use_look_at: bool, use_folders: bool
    ) -> list[Place]:
        self.log.debug("Loading %s", kml_path)
        kml_file = fastkml.kml.KML.parse(kml_path)

        def _collect_places(kml, prefix: list[str]) -> list[Place]:
            if isinstance(kml, fastkml.containers.Folder):
                if (
                    use_folders
                    and kml.view is not None
                    and isinstance(kml.view, fastkml.views.LookAt)
                ):
                    assert kml.name is not None, "Folder name is required"
                    assert kml.view.latitude is not None, "Folder latitude is required"
                    assert (
                        kml.view.longitude is not None
                    ), "Folder longitude is required"
                    assert kml.view.range is not None, "Folder range is required"
                    folder_place = Place(
                        "/".join(prefix + [kml.name]),
                        kml.view.latitude,
                        kml.view.longitude,
                        radius=kml.view.range / 2,
                    )
                    prefix = prefix + [kml.name]
                    return [folder_place] + list(
                        itertools.chain.from_iterable(
                            [_collect_places(f, prefix) for f in kml.features]
                        )
                    )
                assert kml.name is not None, "Folder name is required"
                prefix = prefix + [kml.name]
            elif isinstance(kml, fastkml.containers.Placemark):
                if (
                    use_look_at
                    and kml.view is not None
                    and isinstance(kml.view, fastkml.views.LookAt)
                ):
                    assert kml.name is not None, "Placemark name is required"
                    assert (
                        kml.view.latitude is not None
                    ), "Placemark latitude is required"
                    assert (
                        kml.view.longitude is not None
                    ), "Placemark longitude is required"
                    assert kml.view.range is not None, "Placemark range is required"
                    return [
                        Place(
                            "/".join(prefix + [kml.name]),
                            kml.view.latitude,
                            kml.view.longitude,
                            radius=kml.view.range / 2,
                        )
                    ]
                else:
                    assert kml.name is not None, "Placemark name is required"
                    assert (
                        kml.kml_geometry is not None
                    ), "Placemark geometry is required"
                    assert isinstance(
                        kml.kml_geometry, fastkml.geometry.Point
                    ), "Only Point geometry is supported"
                    assert (
                        kml.kml_geometry.kml_coordinates is not None
                    ), "Point coordinates are required"
                    latitude = kml.kml_geometry.kml_coordinates.coords[0][1]
                    longitude = kml.kml_geometry.kml_coordinates.coords[0][0]
                    radius = (
                        kml.view.range / 2
                        if kml.view is not None
                        and isinstance(kml.view, fastkml.views.LookAt)
                        and kml.view.range is not None
                        else None
                    )
                    return [
                        Place(
                            "/".join(prefix + [kml.name]),
                            latitude,
                            longitude,
                            radius=radius,
                        )
                    ]

            if hasattr(kml, "features"):
                return list(
                    itertools.chain.from_iterable(
                        [_collect_places(f, prefix) for f in kml.features]
                    )
                )
            return []

        places = _collect_places(kml_file, [])

        self.log.debug("Found %d places:", len(places))
        for place in places:
            self.log.debug("%s", place)

        return places

    def process(self, file: File, context: str | None) -> str:
        assert context is not None
        coordinates = Point.from_string(context)
        place = self._find_best_match(self.places, coordinates)
        if place is None:
            return self.default
        return place.name

    @staticmethod
    def _find_best_match(places: list[Place], point: Point) -> Place | None:
        gc = great_circle()

        places_in_range = [
            p
            for p in places
            if p.radius is not None and gc.measure(p.position, point) < p.radius
        ]

        if not places_in_range:
            return None

        # Return place with smallest radius
        return min(places_in_range, key=lambda p: p.radius or float("inf"))

        # min_distance: float = -1
        # min_distance_place: Place | None = None
        #
        # for place in places_in_range:
        #     distance = gc.measure(place.position, point)
        #     if distance > place.radius:
        #         continue
        #     if min_distance_place is None or distance < min_distance:
        #         min_distance = distance
        #         min_distance_place = place
        # return min_distance_place
