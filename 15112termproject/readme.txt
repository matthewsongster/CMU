Description:
Draw Something! Is a multiplayer (2-4 player) drawing game made using python. Similar to skribble.io and the actual game, Draw Something, one player will be the drawing the hidden word as the others try to guess the word by the drawing.

How to Run:
All instances of this game must be on the same network. Before starting, make sure the correct IP address and port is chosen. The port is set to 42042 by default, and can be changed if it is occupied. The IP is set to "localhost" by default and does not need to be changed if running all instances on the same computer. Else, replace the IP with the address of the computer running the server.py file. To do this, check the following:

	- PORT inputs: server.py line 8  AND  Draw_Something.py, line 70
	- IP inputs: server.py line 7  AND  cmu_112_graphics_client.py line 9

To start, run the server.py first. Then run Draw_Something.py for each player. If running multiple programs on one computer, use terminal or cmd and run. MUST BE RUN WITH PYTHON 3.

If app cannot exit, force quit the python programs.

Libraries to install:
- sockets
- threading
- queue
- os
- random
- time
- pip, pillow, requests, tkinter (for cmu_graphics)

Shortcut commands:
None