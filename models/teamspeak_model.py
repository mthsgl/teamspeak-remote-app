from dataclasses import dataclass
import json

@dataclass
class SendPayload:
    button: str
    state: bool

    def __init__(self, button, state):
        self.button = button
        self.state = state

@dataclass
class TeamspeakSend:
    type: str
    payload: SendPayload

    def to_json(self):
        str_json = {
            "type": self.type,
            "payload": {
                "button": self.payload.button,
                "state": self.payload.state
            }
        }
        return json.dumps(str_json)