# Welcome to the Magic Launcher Extra toybox!
The applets and tools in this repository are not officially supported as part of Magic Launcher and their useabilty with it not guaranteed as with any other app.

However, any application that makes it into this repository will be built according to the same paradigm, and have very similar dependencies.

## ML Extras Aspirations

Start instantly
Do one thing well
Work everywhere Python works
No dependencies beyond stdlib (mostly)
Under 500 lines each

## List of Applets

This list is not likely to grow rapidly as I am trying to keep focused on the main game. But sometimes a small idea for a focused tool or toy will occur and so, it will appear here.

### UniText
- A super lightweight text viewer and very basic editor. 
It's good for Unicode as long as there's A font available for it.

### MLSweeper
- What would retro computing be without it? 
Now with boss key! (This is not the way but this is the way).
This solves TWO problems, violating our anti bloat principle BUT...
I built it in fun, and it is still bloody simple. What I did stop myself doing, was taking it beyond a simple boss key.

### JSweeper
- MLSweeper's evil TTS Twin. 
A command-line Minesweeper implementation that outputs the game state as JSON, making it ideal for scripting and automation. 
It shares the same stats file as MLSweeper, you can't hide your shame.

### MLMatrix
- A slow screensaver, bit weird with multiscreen.
Create a password file in ./configure/mlmatrix/lock.txt and you'll need to type in a password to unlock.

#### MLCalc
- A minimal graphical calculator for basic arithmetic.
A last resort for people who can't stand opening a terminal and writing out a statement.

#### MLNonul: 
- The tool you didn't know you needed until PowerShell decided to add null bytes to your CSV.

#### MLJ2C
- Takes two keys from a JSON and pumps them into a CSV to plot. May result in null bytes in your CSV in Powershell.

#### MLPlot
- Create a simple plot from CSV data. It features auto-scaling axes, labels, and a resizable window.
While it works with timeseries as strings will get assigned row numbers, it's built for two number values as input.

#### MlOutput
- A graphical output display for any terminal command. It captures stdout and stderr in real-time, with the ability to pause, clear the log, and apply a regular expression filter to the output.
Magic Launcher tends to have a bit of a recursive terminal going on especially if using it to launch itself in other environments.
This also serves as a very useful way to turn any non-interactive terminal application into a window.

#### MLTimer
- Visual timer with command on conclude.
Clock go tick, command go... go.

#### SequAI
Passes the shortcuts.json from MLMenu and your request to an OpenAI compatible completions API and asks it to present the correct sequence of numbers to run commands that complete your request.
Intended as a demo of composition being a better way to use a service than bespoke integration.
100% experimental, but it demos the concept.