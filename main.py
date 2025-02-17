import asyncio
import tkinter as tk
from views.main_window import MainWindow

async def async_main():
    window = MainWindow()
    
    # Créer une tâche pour exécuter la boucle Tkinter
    def tk_update():
        window.root.update()
        loop.call_later(1/30, tk_update)  # Met à jour l'interface 30 fois par seconde
    
    loop = asyncio.get_event_loop()
    loop.call_soon(tk_update)
    try:
        while True:
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        window.root.quit()
        loop.stop()

if __name__ == "__main__":
    asyncio.run(async_main())
