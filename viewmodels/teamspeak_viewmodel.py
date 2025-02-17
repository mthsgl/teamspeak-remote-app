import json
import asyncio
import websockets
from typing import Optional, Callable
import dotenv

from models.midi_device import MidiMessage
from mediators.event_mediator import EventMediator, EventType
from utils.utils import APP_NAME
from models.teamspeak_model import SendPayload, TeamspeakSend

class TeamspeakViewModel:
    def __init__(self, mediator: EventMediator):
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.app_identifier = APP_NAME
        self.connected = False
        self.mediator = mediator

        self.set_callbacks()

    def set_callbacks(self):
        self.mediator.subscribe(EventType.MUTE_PRESSED, self.on_mute_pressed)
        self.mediator.subscribe(EventType.DEAF_PRESSED, self.on_deaf_pressed)
        self.mediator.subscribe(EventType.AFK_PRESSED, self.on_afk_pressed)
        self.mediator.subscribe(EventType.PUSH_TO_TALK, self.on_push_to_talk)
        self.mediator.subscribe(EventType.PUSH_TO_MUTE, self.on_push_to_mute)
        self.mediator.subscribe(EventType.STREAM_CAPTURE, self.on_stream_capture)
        
    async def connect(self):
        try:
            self.ws = await websockets.connect("ws://localhost:5899")
            api_key = self.get_api_key()

            auth_payload = {
                "type": "auth",
                "payload": {
                    "identifier": self.app_identifier,
                    "version": "0.1",
                    "name": "Python TeamSpeak Remote",
                    "description": "Remote control app for TeamSpeak",
                    "content": {
                        "apiKey": api_key
                    }
                }
            }

            await self.ws.send(json.dumps(auth_payload))
                
            asyncio.create_task(self._listen_websocket(api_key))
        except Exception as e:
            print(f"Erreur de connexion: {e}")
                
    async def disconnect(self):
        if self.ws:
            await self.ws.close()
            self.mediator.publish(EventType.CONNECTION_CHANGED, False)
    
    def get_api_key(self) -> str:
        dotenv.load_dotenv()
        api_key = dotenv.get_key(".env", "API_KEY")
        return api_key if api_key else ""

                
    async def _listen_websocket(self, api_key: str):
        while True:
            try:
                message = await self.ws.recv()
                message = json.loads(message)

                # Traiter les messages reçus ici
                print(f"Message reçu: {json.dumps(message, indent=4)}")
                
                # Stockage de la clé API pour ne plus avoir à authoriser l'application dans TeamSpeak
                if api_key == "" and message['payload']['apiKey']:
                    dotenv.set_key(".env", "API_KEY", message['payload']['apiKey'])

                # Vérification de connexion et envoi de l'évenement à l'UI
                if message['type'] == "auth" and message['status']['message'] == "ok":
                    self.mediator.publish(EventType.CONNECTION_CHANGED, True)
                    self.connected = True

            except websockets.exceptions.ConnectionClosed:
                self.mediator.publish(EventType.CONNECTION_CHANGED, False)
                self.connected = False
                break
            except Exception as e:
                print(f"Erreur lors de l'écoute: {e}")

    async def on_mute_pressed(self, message:MidiMessage):
        try:
            await self.send_button_press(message, "mute")
        except Exception as e:
            print(f"Erreur lors de l'envoi de la commande: {e}")


    async def on_deaf_pressed(self, message:MidiMessage):
        try:
            await self.send_button_press(message, "deaf")
        except Exception as e:
            print(f"Erreur lors de l'envoi de la commande: {e}")
    
    async def on_afk_pressed(self, message:MidiMessage):
        try:    
            await self.send_button_press(message, "afk")
        except Exception as e:
            print(f"Erreur lors de l'envoi de la commande: {e}")

    async def on_push_to_mute(self, message:MidiMessage):
        try:      
            await self.send_button_press(message, "push_to_mute")
        except Exception as e:
            print(f"Erreur lors de l'envoi de la commande: {e}")

    async def on_push_to_talk(self, message:MidiMessage):
        try:    
            await self.send_button_press(message, "push_to_talk")
        except Exception as e:
            print(f"Erreur lors de l'envoi de la commande: {e}")

    async def on_stream_capture(self, message:MidiMessage):
        try:    
            await self.send_button_press(message, "stream_capture")
        except Exception as e:
            print(f"Erreur lors de l'envoi de la commande: {e}")

    
    async def send_button_press(self, message: MidiMessage, buttonName: str):
        if not self.ws or not self.connected:
            print("Vous n'êtes pas connecté")
            return
        message_to_send = None
        if message.data_byte_2 == 127:
            message_to_send = TeamspeakSend("buttonPress", SendPayload(buttonName, True))
        else:
            message_to_send = TeamspeakSend("buttonPress", SendPayload(buttonName, False))      
        await self.ws.send(message_to_send.to_json())
