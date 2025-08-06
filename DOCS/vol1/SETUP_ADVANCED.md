#### Setup for easy launch with WSL

#### For Git Users

Paste to set up with git:
- BASH (Linux/WSL)
```bash
#!/bin/bash
git clone https://github.com/Bladetrain3r/Magic-Launcher.git ~/.local/share/Magic-Launcher
echo 'alias mlmain="python3 ~/.local/share/Magic-Launcher/launcher/app.py"' >> ~/.bashrc
# To launch on login
echo 'if [ -n "$DISPLAY" ]; then mlmain & fi' >> ~/.bashrc
```

Quick Setup in Windows Powershell:
```From Powershell
git clone "https://github.com/Bladetrain3r/Magic-Launcher.git" ~/.local/share/Magic-Launcher
Write-Output "function MagicLaunch {python ~/.local/share/Magic-Launcher/launcher/app.py}" | Out-File -FilePath $profile
MagicLaunch
# To run from the "Run" menu or cmd
# powershell -Noninteractive MagicLaunch
```

#### Shortcut in Windows
Create a shortcut to Python and append "app.py" to the end of the target.
Under "Start in" paste the path to the folder containing app.py
![Windows Shortcut](image-1.png)

A quick setup script is in the roadmap.