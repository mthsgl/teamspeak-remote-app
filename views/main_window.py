import tkinter as tk
from tkinter import ttk
import json
import asyncio
from models.midi_device import MidiDevice, MidiMessage
from viewmodels.midi_viewmodel import MidiViewModel
from viewmodels.teamspeak_viewmodel import TeamspeakViewModel
from mediators.event_mediator import EventMediator, EventType

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TeamSpeak Remote MIDI")
        self.root.geometry("400x250")

        # Initialiser la boucle asyncio
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Mediateur
        self.mediator = EventMediator()
        
        # ViewModels
        self.midi_vm = MidiViewModel(self.mediator)
        self.teamspeak_vm = TeamspeakViewModel(self.mediator)
        
        # Variables
        self.device_var = tk.StringVar()
        self.connection_status_var = tk.StringVar(value="Déconnecté")
        self.captured_message_var = tk.StringVar(value="Aucun message capturé")
        
        self._init_ui()
        self._setup_callbacks()
        
    def _init_ui(self):
        # Frame MIDI
        midi_frame = ttk.LabelFrame(self.root, text="MIDI", padding=10)
        midi_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Sélecteur de périphérique MIDI
        ttk.Label(midi_frame, text="Périphérique:").pack(anchor=tk.W)
        self.device_combo = ttk.Combobox(midi_frame, textvariable=self.device_var)
        self.device_combo.pack(fill=tk.X)  
        
        # Bouton de connexion
        self.connection_button = ttk.Button(midi_frame, text="Connecter", 
                                       command=self._on_device_selected)
        self.connection_button.pack(pady=5)
        
        # Frame TeamSpeak
        ts_frame = ttk.LabelFrame(self.root, text="TeamSpeak", padding=10)
        ts_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Status et bouton de connexion
        self.connect_button = ttk.Button(ts_frame, text="Connecter", 
                                       command=self._toggle_connection)
        self.connect_button.pack(pady=5)
        
        # Rafraîchir la liste des périphériques
        self._refresh_devices()

    
        
    def _setup_callbacks(self):
        self.mediator.subscribe(EventType.CONNECTION_CHANGED, self._on_connection_changed)
        self.device_combo.bind('<<ComboboxSelected>>', self._on_device_selected)
        
    def _refresh_devices(self):
        devices = self.midi_vm.get_available_devices()
        
        self.device_combo['values'] = [device.name for device in devices]
        if devices:
            self.device_combo.current(0)
            
    def _on_device_selected(self):
        selected_name = self.device_var.get()
        devices = self.midi_vm.get_available_devices()
        selected_device = next((d for d in devices if d.name == selected_name), None)
        
        if selected_device:
            self.midi_vm.connect_device(selected_device)
            self.connection_button['text'] = "Connecté"
        
        self.midi_vm.select_device_out(selected_device)
        
    def _toggle_connection(self):
        self.connect_button['text'] = "Connexion..."
        loop = asyncio.get_event_loop()
        loop.create_task(self.teamspeak_vm.connect())
            
    def _on_connection_changed(self, connected: bool):
        if connected:
            self.connect_button['text'] = "Connecté"
        else:
            self.connect_button['text'] = "Connecter"
        
    def run(self):
        self.root.mainloop()