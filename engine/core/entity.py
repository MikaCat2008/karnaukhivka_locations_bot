from __future__ import annotations

from typing import Type, TypeVar, Optional, TYPE_CHECKING
from collections import deque

if TYPE_CHECKING:
    from .component import Component

ComponentType = TypeVar("ComponentType", bound="Component")


class Entity:
    childs: deque[Entity]
    components: dict[str, Component]

    def __init__(self) -> None:
        self.childs = deque()
        self.components = {}
        
    def add_component(self, component: Component) -> None:
        self.components[type(component).__name__] = component

    def get_component(self, component: Type[ComponentType]) -> Optional[ComponentType]:
        return self.components.get(component.__name__)

    def remove_component(self, component: Type[ComponentType]) -> None:
        del self.components[component.__name__]
