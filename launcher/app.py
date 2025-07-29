def check_dependencies():
    """Check for required dependencies."""
    import sys
    try:
        import tkinter
    except ImportError:
        print("Error: tkinter is not installed.")
        print("\nInstall tkinter:")
        print("  Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  Fedora: sudo dnf install python3-tkinter")
        print("  Arch: sudo pacman -S tk")
        print("  Amazon Linux: yum install python3-tkinter")
        print("  macOS: tkinter should be included with Python")
        print("\nFor Docker containers, add to Dockerfile:")
        print("  RUN apt-get update && apt-get install -y python3-tk")
        sys.exit(1)

if __name__ == "__main__":
    check_dependencies()

# Logic BEFORE imports?! Blasphemy.
import os
import tkinter as tk
from ui.main_window import MainWindow
from utils.logger import logger
from constants import VERSION
from config import ConfigManager

class LauncherApp:
    """Main application controller."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.main_window = None

        # Check for MLENV environment variable
        if 'MLENV' in os.environ:
            if os.environ['MLENV'] == 'dev':
                logger.setLevel("DEBUG")
            else:
                logger.setLevel("INFO")
        
        # Optional but nice to have
        try:
            from PIL import Image
        except ImportError:
            print("Note: Pillow not installed. BMP icon support disabled.")
            print("  Install with: pip install Pillow")
            print()  # Just a warning, don't exit

    def run(self):
        """Run the application."""
        try:
            logger.info(f"Starting {ConfigManager.get_app_name(self)} v{VERSION}")

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
    # Check dependencies before starting
    LauncherApp().check_dependencies()
    main()