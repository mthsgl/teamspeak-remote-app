from math import e
from re import S
import ssl
import time
from typing import List, Optional, Callable
import rtmidi
from models.midi_device import MidiDevice, MidiMessage
from mediators.event_mediator import EventMediator, EventType

class MidiViewModel:
    def __init__(self, mediator: EventMediator):
        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()
        self.device_out: MidiDevice = None
        self.current_device: Optional[MidiDevice] = None
        self.running = False
        self.on_message_captured: Optional[Callable[[MidiMessage], None]] = None
        self.on_mute_pressed: Optional[Callable[[MidiMessage, None]]] = None
        self.mediator = mediator

        self.is_muted: bool = None
        self.is_deaf: bool = None
        self.is_afk: bool = None
        self.is_stream: bool = None
        
    def get_available_devices(self) -> List[MidiDevice]:
        devices = []
        port_names = self.midi_in.get_ports()
        for i, name in enumerate(port_names):
            devices.append(MidiDevice(i, name))
        return devices

    def select_device_out(self, device_in: MidiDevice):
        port_names = self.midi_out.get_ports()
        for i, name in enumerate(port_names):
            device = MidiDevice(i, name)
            if device.name.startswith(device_in.name.split()[0]):
                self.midi_out.open_port(device.port_number)
                pass
    
    def connect_device(self, device: MidiDevice) -> None:
        if self.current_device is not None:
            self.disconnect_device()
        self.midi_in.open_port(device.port_number)
        self.current_device = device
        self.running = True
        self.midi_in.set_callback(self._midi_callback)
        self.midi_in.ignore_types(False, False, False)
        
    def disconnect_device(self) -> None:
        if self.current_device is not None:
            self.midi_in.close_port()
            self.current_device = None
            self.running = False
    
    def handle_mute(self, message:MidiMessage) -> None:
        self.mediator.publish(EventType.MUTE_PRESSED, message)
        if (message.data_byte_2 == 0):
            return
        if not self.is_muted:
            self.turn_on_light(message)
            self.is_muted = True
        else:
            self.turn_off_light(message)
            self.is_muted = False
    
    def handle_deaf(self, message:MidiMessage) -> None:
        self.mediator.publish(EventType.DEAF_PRESSED, message)
        if (message.data_byte_2 == 0):
            return
        if not self.is_deaf:
            self.turn_on_light(message)
            self.is_deaf = True
        else:
            self.turn_off_light(message)
            self.is_deaf = False

    def handle_afk(self, message:MidiMessage) -> None:
        self.mediator.publish(EventType.AFK_PRESSED, message)
        if (message.data_byte_2 == 0):
            return
        if not self.is_afk:
            self.turn_on_light(message)
            self.is_afk = True
        else:
            self.turn_off_light(message)
            self.is_afk = False
    
    def handle_push_to_mute(self, message:MidiMessage) -> None:
        self.mediator.publish(EventType.PUSH_TO_MUTE, message)
        if message.data_byte_2 == 127:
            self.turn_on_light(message)
        else: 
            self.turn_off_light(message)
        
    def handle_push_to_talk(self, message:MidiMessage) -> None:
        self.mediator.publish(EventType.PUSH_TO_TALK, message)
        if message.data_byte_2 == 127:
            self.turn_on_light(message)
        else: 
            self.turn_off_light(message)
    
    def handle_stream_capture(self, message:MidiMessage) -> None:
        self.mediator.publish(EventType.STREAM_CAPTURE, message)
        if (message.data_byte_2 == 0):
            return
        if not self.is_stream:
            self.turn_on_light(message)
            self.is_stream = True
        else:
            self.turn_off_light(message)
            self.is_stream = False

    def turn_on_light(self, message:MidiMessage):
        try:
            self.midi_out.send_message([message.status_byte, message.data_byte_1, 127])
        except Exception as e:
            print("Error sending message : ", e)

    def turn_off_light(self, message:MidiMessage):
        try:
            self.midi_out.send_message([message.status_byte, message.data_byte_1, 0])
        except Exception as e:
            print("Error sending message : ", e)
        
    def _midi_callback(self, message, data=None):
        midi_message = MidiMessage(status_byte=message[0][0], data_byte_1=message[0][1], data_byte_2=message[0][2], timestamp=message[1])
        if not midi_message.status_byte == 151 and not midi_message.status_byte == 146:
            return
        match midi_message.data_byte_1:
            case 0:
                self.handle_mute(midi_message)
            case 1:
                self.handle_deaf(midi_message)
            case 2:
                self.handle_afk(midi_message)
            case 3:
                self.handle_push_to_mute(midi_message)
            case 7:
                self.handle_push_to_talk(midi_message)
            case 6:
                self.handle_stream_capture(midi_message)
            case _:
                pass
