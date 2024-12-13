from dataclasses import dataclass

from engine.core import Component


@dataclass
class LocationComponent(Component):
    id: int
    name: str


@dataclass
class LocationFilesComponent(Component):
    files: list[str]


@dataclass
class LocationRatingComponent(Component):
    likes: int
    dislikes: int
