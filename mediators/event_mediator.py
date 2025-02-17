from typing import Dict, List, Callable
from enum import Enum, auto
import asyncio

class EventType(Enum):
    MUTE_PRESSED = auto()
    DEAF_PRESSED = auto()
    AFK_PRESSED = auto()
    CONNECTION_CHANGED = auto()
    PUSH_TO_TALK = auto()
    PUSH_TO_MUTE = auto()
    STREAM_CAPTURE = auto()

class EventMediator:
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._loop = asyncio.get_event_loop()
        
    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        
    def publish(self, event_type: EventType, *args, **kwargs) -> None:
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                if asyncio.iscoroutinefunction(callback):
                    self._loop.create_task(callback(*args, **kwargs))
                else:
                    callback(*args, **kwargs)