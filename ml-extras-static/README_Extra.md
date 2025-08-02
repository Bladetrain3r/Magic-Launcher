# Welcome to the Magic Launcher Extra toybox!
The applets and tools in this folder are not officially supported as part of Magic Launcher and their useabilty with it not guaranteed as with any other app.
However, any application that makes it into this repository will be built according to the same paradigm, and have very similar dependencies.

## ML Extras Aspirations

Start instantly
Do one thing well
Work everywhere Python works
No dependencies beyond stdlib (mostly)
Under 500 lines each

## List of Applets

This list is not likely to grow rapidly as I am trying to keep focused on the main story as it were. But sometimes a small idea for a focused tool or toy will occur and so, it will appear here.

### UniText
- A super lightweight text viewer and very basic editor. 
It's good for Unicode as long as there's A font available for it.

### MLSweeper
- What would retro computing be without it? 
Now with boss key! (This is not the way but this is the way).
This solves TWO problems, violating our anti bloat principle BUT...
I built it in fun, and it is still bloody simple. What I did stop myself doing, was taking it beyond a simple boss key.

#### MLCalc
- A minimal graphical calculator for basic arithmetic.
~~A last resort for people who can't stand opening a terminal and writing out a statement.~~

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
~~Clock go tick, command go... go.~~