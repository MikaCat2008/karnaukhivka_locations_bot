from .start import Bot_StartHandlersSystem
from .admin import Bot_AdminHandlersSystem
from .details import Bot_DetailsHandlersSystem
from .suggest import Bot_SuggestHandlersSystem
from .location import Bot_LocationHandlersSystem


SYSTEMS = [
    Bot_StartHandlersSystem(),
    Bot_AdminHandlersSystem(),
    Bot_DetailsHandlersSystem(),
    Bot_SuggestHandlersSystem(),
    Bot_LocationHandlersSystem()
]
