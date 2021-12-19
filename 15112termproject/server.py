'''
#server file
#SOURCE: 15112 CMU WEBSITE: TA LED MINI LECTURES SOCKET VIDEO

import socket
import threading
from queue import Queue
HOST = socket.gethostbyname("localhost")
PORT = 42042
BACKLOG = 4
                     
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Below line makes address reusable.
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST,PORT))
server.listen(BACKLOG) 

print("looking for connection")
messageSeperator = "\n"

def handleClient(client, serverChannel, cID, clientele):
  client.setblocking(1)
  msg = ""
  while True:
    try:
      msg += client.recv(10).decode("UTF-8")
      command = msg.split(messageSeperator)
      while (len(command) > 1):
        readyMsg = command[0]
        msg = messageSeperator.join(command[1:])
        serverChannel.put(str(cID) + "_" + readyMsg)
        command = msg.split(messageSeperator)
    except:
      clientele.pop(cID)
      return

def serverThread(clientele, serverChannel):
  while True:
    msg = serverChannel.get(True, None)
    print("msg recv: ", msg)
    senderID, msg = int(msg.split("_")[0]), "_".join(msg.split("_")[1:])
    if (msg):
      for cID in clientele:
        if cID != senderID:
          sendMsg = str(senderID) + " " + msg + messageSeperator
          clientele[cID].send(sendMsg.encode())
    serverChannel.task_done()

clientele = {}
currID = 0

serverChannel = Queue(100)
threading.Thread(target = serverThread, args = (clientele, serverChannel)).start()

while True:
  client, address = server.accept()
  print(currID)
  for cID in clientele: 
    
    print (repr(cID), repr(currID))
    clientele[cID].send(f"newPlayer {currID} 100 100{messageSeperator}".encode())
    client.send(f"newPlayer {cID} 100 100{messageSeperator}".encode())
  clientele[currID] = client
  print("connection recieved")
  threading.Thread(target = handleClient, args = 
                        (client ,serverChannel, currID, clientele)).start()
  currID += 1
'''


# 1. Assign these values from your Autolab gradebook:
hwAvg      = 99.5
collabAvg  = 99.9
quizAvg    = 77.8
midtermAvg = 86.9

# 2. Then pick these values based on your expected grades:
final = midtermAvg         # the default if you do not opt-in to take the final
tp = 89.6                    # your tp3 grade.  You can try different values...
passedParticipation = True # Set this to False if needed

# 3. Then run this to see your standard (non-AMG) grade computation:
divisor = 0.9 if passedParticipation else 1.0
grade = (0.10*quizAvg +
         0.15*hwAvg +
         0.20*collabAvg +
         0.15*midtermAvg +
         0.20*tp +
         0.10*final) / divisor

print(f'Standard (non-AMG) grade: {round(grade, 1)}')

if (grade < 70):
    print('Please recompute using the AMG grade computation.')
    print('See syllabus for details.')