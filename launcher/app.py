"""Main application class for Magic Launcher."""

import tkinter as tk
from ui.main_window import MainWindow
from utils.logger import logger
from constants import APP_NAME, VERSION


class LauncherApp:
    """Main application controller."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.main_window = None
        
    def run(self):
        """Run the application."""
        try:
            logger.info(f"Starting {APP_NAME} v{VERSION}")
            
            # Create main window
            self.main_window = MainWindow(self.root)
            
            # Start main loop
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            raise
        finally:
            logger.info("Application closed")


def main():
    """Entry point."""
    app = LauncherApp()
    app.run()


if __name__ == "__main__":
    main()