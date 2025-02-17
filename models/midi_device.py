from dataclasses import dataclass
from typing import Optional

@dataclass
class MidiDevice:
    port_number: int
    name: str
    
@dataclass
class MidiMessage:
    status_byte: int
    data_byte_1: int
    data_byte_2: int
    timestamp: float
    
    def init(self, status_byte:int, data_byte_1: int, data_byte_2:int, timestamp: float):
        self.status_byte = status_byte
        self.data_byte_1 = data_byte_1
        self.data_byte_2 = data_byte_2
        self.timestamp = timestamp

    def __str__(self):
        return f"Message: {self.status_byte} {self.data_byte_1} {self.data_byte_2}, Timestamp: {self.timestamp}"


