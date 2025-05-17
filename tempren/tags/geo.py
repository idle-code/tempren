import itertools
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import fastkml.kml
from geopy import Point
from geopy.distance import great_circle

from tempren.primitives import File, Tag


@dataclass
class Place:
    name: str
    latitude: float
    longitude: float
    radius: Optional[float]

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
    places: List[Place]
    default: str

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def configure(
        self,
        kml: str,
        use_look_at: bool = True,
        use_folders: bool = True,
        default: str = "",
        to_csv: Optional[str] = None,
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
                        f"{p.latitude}, {p.longitude}, {p.radius / 1000}, {p.name}\n"
                        for p in self.places
                    ]
                )

    def _load_file(
        self, kml_path: str, use_look_at: bool, use_folders: bool
    ) -> List[Place]:
        self.log.debug("Loading %s", kml_path)
        kml_file = fastkml.kml.KML.parse(kml_path)

        def _collect_places(kml, prefix: List[str]) -> List[Place]:
            if isinstance(kml, fastkml.containers.Folder):
                if use_folders and kml.view is not None:
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
                prefix = prefix + [kml.name]
            elif isinstance(kml, fastkml.containers.Placemark):
                if use_look_at and kml.view is not None:
                    return [
                        Place(
                            "/".join(prefix + [kml.name]),
                            kml.view.latitude,
                            kml.view.longitude,
                            radius=kml.view.range / 2,
                        )
                    ]
                else:
                    latitude = kml.kml_geometry.kml_coordinates.coords[0][0]
                    longitude = kml.kml_geometry.kml_coordinates.coords[0][1]
                    radius = kml.view.range if kml.view / 2 is not None else None
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

    def process(self, file: File, context: Optional[str]) -> str:
        assert context is not None
        coordinates = Point.from_string(context)
        place = self._find_best_match(self.places, coordinates)
        if place is None:
            return self.default
        return place.name

    @staticmethod
    def _find_best_match(places: List[Place], point: Point) -> Optional[Place]:
        gc = great_circle()

        places_in_range = filter(
            lambda p: gc.measure(p.position, point) < p.radius, places
        )

        # FIXME: Fix the types
        smallest_place_in_range = next(
            sorted(places_in_range, key=lambda p: p.radius), None
        )
        return smallest_place_in_range

        # min_distance: float = -1
        # min_distance_place: Optional[Place] = None
        #
        # for place in places_in_range:
        #     distance = gc.measure(place.position, point)
        #     if distance > place.radius:
        #         continue
        #     if min_distance_place is None or distance < min_distance:
        #         min_distance = distance
        #         min_distance_place = place
        # return min_distance_place
