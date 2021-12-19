#server client + graphics file
#SOURCE: 15112 CMU WEBSITE: TA LED MINI LECTURES SOCKET VIDEO

from cmu_112_graphics import *
import socket, threading
from queue import Queue

class AppWithSockets(TopLevelApp):
    def turnOnSockets(self, port, IP = "localhost"):
        self.msgSeperator = "\n"
        self.serverMsg = Queue(100)
        self.imOn = False
        if(not self.startSocket(port, IP)):
            return False
        else:
            print("Connected")
            self.imOn = True
            return True
    def startSocket(self, port, IP):
        try:
        	self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        	self.server.connect((IP, port))
        except:
            print(f"Invalid IP: {IP} with Port {port}")
            return False
        threading.Thread(target = self.handleServerMessage).start()
        return True

    def handleServerMessage(self):
        self.server.setblocking(1)
        msg = ""
        command = ""
        while True:
            msg += self.server.recv(10).decode("UTF-8")
            command = msg.split(self.msgSeperator)
            while(len(command) > 1):
                readyMsg = command[0]
                msg = self.msgSeperator.join(command[1:])
                self.serverMsg.put(readyMsg)
                command = msg.split(self.msgSeperator)

    def getOldestUnreadMessage(self):
        if(self.serverMsg.qsize() > 0):
            msg = self.serverMsg.get(False)
            print(f"received {msg}")
            self.serverMsg.task_done()
            return msg

    def sendMessage(self, message):
        print(f"Sending {message}")
        self.server.send((message + self.msgSeperator).encode())



"""
More Sockets Info:
Github Page:
https://kdchin.gitbooks.io/sockets-module-manual/content/running-sockets.html



Additional info about OOP:

See Course Notes at links for General Info:
http://www.cs.cmu.edu/~112/notes/notes-oop-part1.html
http://www.cs.cmu.edu/~112/notes/notes-oop-part2.html
http://www.cs.cmu.edu/~112/notes/notes-oop-part3.html



The line: AppWithSockets(TopLevelApp)
https://www.kosbie.net/cmu/spring-20/15-112/notes/
notes-animations-part2.html#subclassingApp
for more info on subclassing App (Note this code is subclassing
TopLevelApp instead of App, so that you can write your graphics code
in a non-OOP style).






"""