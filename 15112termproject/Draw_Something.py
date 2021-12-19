#Main python file

from cmu_112_graphics_client import *
import os, random, time

#line to fix relative path errors
#SOURCE: https://stackoverflow.com/questions/43396378/pillow-file-not-found
my_path = os.path.dirname(__file__)

#helper function to extract list of leaderboard text from file
def leaderboard():
    f = open(my_path + "/Leaderboard.txt", "r")
    text = f.read().splitlines()
    f.close()
    return text

#helper function to extract list of words from WordBank.txt file
def wordBank():
    f = open(my_path + "/WordBank.txt", "r")
    text = f.read().split(",")
    for i in range(len(text)): #word in text:
        text[i] = text[i].upper() #word = word.upper()
        text[i] = text[i].strip() #word = word.strip()
    f.close()
    return text

#helper function to show word in hidden form like "_ _ _..."
def hiddenWord(word):
    hidden = "Word: "
    for letter in word:
        if letter.isalpha:
            hidden += "_ "
        else:
            hidden += letter
    return hidden

#helper function to calculate input word difficulty
def wordDiff(word):
    if len(word) >= 8:
        return 3
    elif 5 <= len(word) <= 7:
        return 2
    else:
        return 1

class MyApp(AppWithSockets):
    #MODEL FUNCTIONS------------------------------------------------------------

    #model function
    def appStarted(self):
        self.timerDelay = 1
        self.beginningName = True
        self.image = self.scaleImage(self.loadImage(my_path + "/image.gif"), 1/6)
        self.playButton = (550,520,650,580)
        self.backButton = (self.width/2-50,520,self.width/2+50,580)
        self.wordButton = (350,520,450,580)
        self.drawSpace = (400, 100, 950, 500)
        self.chatSpace = (50, 300, 350, 550)
        self.toolSpace = (400, 500, 950, 550)
        self.colors = ["black", "blue", "green", "yellow", "red", "white"]
        self.thicknesses = [1,2,3,4,6,8]
        self.name = ""
        self.names = []
        self.restart()
        self.serverStuff()
        
    #helper model function for server setup
    #SOURCE: 15112 CMU WEBSITE: TA LED MINI LECTURES SOCKET VIDEO
    def serverStuff(self):
        self.turnOnSockets(42042)
        self.commandSeperator = " "
        self.otherPlayerID = []
    
    #helper model function called when restarting game
    def restart(self):
        self.gameOver = False
        self.starting = True
        self.wordBanking = False
        self.wording = False
        self.playing = False
        self.turn = 0
        self.round = 1
        self.score = [0,0,0,0]
        self.diff = 1
        self.roundRestart()
    
    #helper model function called when next round starts
    def roundRestart(self):
        self.roundTime = 60
        self.color = "black"
        self.wordTime = 7
        self.lookAwaying = True
        self.words = []
        self.word = ""
        self.chatline = ""
        self.chatlog = []
        self.chatIndex = 0
        self.wins = 0
        self.tempWinning = False
        self.winning = False
        self.tool = 0
        self.tool2 = 2
        self.tool3 = True
        self.board = [([5]*55) for row in range(40)]
        self.lines = []

    #CONTROLLER FUNCTIONS-------------------------------------------------------
    
    #helper cont. function adding to total score at end of each round
    def roundScore(self):
        for i in range(len(self.names)):
            if self.turn == i:
                if self.winning:
                    self.score[i] += 100 - (60 - int(self.roundTime))+10*wordDiff(self.word)
                else:
                    self.score[i] += 20
            else:
                if self.winning:
                    self.score[i] += 85 - (60 - int(self.roundTime))

    #helper cont. function generating list of words randomly from wordBank
    def wordsGenerator(self):
        while len(self.words) < 3:
            newWord = random.choice(wordBank())
            if newWord not in self.words:
                for i in range(1,4):
                    if self.diff == wordDiff(newWord) == i:
                        self.words.append(newWord)

    #helper cont. function changing turn after each round
    def changeTurn(self):
        self.turn += 1
        if self.turn == len(self.otherPlayerID)+1:
            self.turn = 0
    
    #helper cont. function that updates leaderboard text file after game end
    def changeLeaderboard(self):
        maxIndex = 0
        maxScore = 0
        for i in range(len(self.score)):
            if self.score[i] >= maxScore:
                maxIndex = i
                maxScore = self.score[i]
        L = leaderboard()
        os.remove(my_path + "/Leaderboard.txt")
        for i in range(len(L)):
            if self.score[maxIndex] >= int(L[i][10: L[i].index(",")]):
                L.insert(i, (L[i][0:10] + str(self.score[maxIndex]) + ", " + self.names[maxIndex]))
                L.pop()
                break
        for i in range(len(L)):
            if (int(L[i][0]) != (i+1)):
                L[i] = str(i+1) + L[i][1:]
        f = open(my_path + "/Leaderboard.txt", "w")
        for line in L:
            f.write(line + "\n") 
        f.close()
    

    #helper cont. function that recursively changes pixels for floodfill mode
    def recursiveBrush(self, col, row, depth):
        #floodfill pixel idea SOURCE: https://youtu.be/2HTbGsXmDQc
        if depth == 0:
            pass
        elif ((0 <= col < 55) and (0 <= row < 40)):
            self.board[row][col] = self.tool
            self.recursiveBrush(col+1, row, depth-1)
            self.recursiveBrush(col-1, row, depth-1)
            self.recursiveBrush(col, row+1, depth-1)
            self.recursiveBrush(col, row-1, depth-1)

    #cont. function called when time goes on
    def timerFired(self):
        if self.beginningName:
            self.name = self.getUserInput("Name:")
            if (self.name == None) or (self.name == ""):
                pass
            else:
                self.beginningName = False
                msg = "name " + self.name
                self.sendMessage(msg)
                self.names.append(self.name)
        elif self.wording:
            self.wordTime -= 0.01
            if self.wordTime < 0:
                self.word = self.words[1]
                self.playing = True
                self.wording = False
        elif self.playing:
            if self.gameOver or self.winning:
                pass
            else:
                self.roundTime -= 0.05
                if self.name == self.names[self.turn] and (int(self.roundTime)%3 == 0):
                    self.sendMessage("time " + str(self.roundTime))
                if self.roundTime < 0:
                    self.gameOver = True
                    self.roundScore()
        #SOURCE: 15112 CMU WEBSITE: TA LED MINI LECTURES SOCKET VIDEO
        msg = self.getOldestUnreadMessage()
        if (msg != None):
            print(msg)
            if msg.startswith("newPlayer"):
                msg = msg.split(self.commandSeperator)
                newPID = int(msg[1])
                print(newPID)
                self.otherPlayerID.append(newPID)
            else:
                msg = msg.strip()
                msg = msg.split(self.commandSeperator)
                if msg[1] == "name":
                    self.names.append(msg[2])
                elif (msg[0] == "0") and (msg[1] == "names"):
                    self.names = []
                    for i in range(len(msg)-2):
                        self.names.append(msg[i+2])
                elif msg[1] == "words":
                    for i in range(len(msg)-2):
                        self.words.append(msg[i+2])
                    self.lookAwaying = False
                    self.wording = True
                elif msg[1] == "word":
                    self.word = msg[2]
                    self.wording = False
                    self.playing = True
                elif msg[1] == "tool":
                    self.tool = int(msg[2])
                    self.color = self.colors[self.tool]
                elif msg[1] == "tool2":
                    self.tool2 = int(msg[2])
                elif msg[1] == "tool3":
                    self.tool3 = not self.tool3
                    self.board = [([5]*55) for row in range(40)]
                    self.lines = []
                elif msg[1] == "board":
                    temp = []
                    self.board = []
                    for i in range(len(msg)-2):
                        if (i+1)%55 == 0:
                            temp.append(int(msg[i+2]))
                            self.board.append(temp)
                            temp = []
                        else:
                            temp.append(int(msg[i+2]))
                elif msg[1] == "lineStop":
                    self.lines.append(0)
                elif msg[1] == "lines":
                    self.lines.append((int(msg[2]),int(msg[3]),int(msg[4]), msg[5]))
                elif msg[1] == "chatSend":
                    line = ""
                    for i in range(len(msg)-2):
                        line += msg[i+2] + " "
                    self.chatlog.append(self.names[int(msg[0])] + ": " + line)
                    if len(self.chatlog) >= 12:
                        self.chatIndex = len(self.chatlog)-11
                elif msg[1] == "wins":
                    self.wins += 1
                    self.chatlog.append(self.names[int(msg[0])] + " guessed the word!")
                elif msg[1] == "winning":
                    self.winning = True
                    self.roundTime = 60
                    self.tool = 0
                    self.tool2 = 2
                    self.tool3 = True
                    self.board = [([5]*55) for row in range(40)]
                    self.lines = []
                elif msg[1] == "diff":
                    self.diff = int(msg[2])
                elif msg[1] == "score":
                    self.score = [int(msg[2]),int(msg[3]),int(msg[4]), int(msg[5])]
                elif msg[1] == "time":
                    self.roundTime = float(msg[2])


    #cont. function called when mouse is clicked at certain stages of game
    def mousePressed(self, event):
        if self.starting:
            if ((self.playButton[0] <= event.x <= self.playButton[2]) and
            (self.playButton[1] <= event.y <= self.playButton[3])):
                self.lookAwaying = True
                self.starting = False
                names = ""
                for name in self.names:
                    names += (name + " ")
                self.sendMessage("names " + names)
            elif ((self.wordButton[0] <= event.x <= self.wordButton[2]) and
            (self.wordButton[1] <= event.y <= self.wordButton[3])):
                self.wordBanking = True
                self.starting = False
        elif self.wordBanking:
            if ((self.backButton[0] <= event.x <= self.backButton[2]) and
            (self.backButton[1] <= event.y <= self.backButton[3])):
                self.starting = True
                self.wordBanking = False
        elif self.lookAwaying:
            if self.name == self.names[self.turn]:
                if ((self.backButton[0] <= event.x <= self.backButton[2]) and
                (self.backButton[1] <= event.y <= self.backButton[3])):
                    self.wordsGenerator()
                    self.wording = True
                    self.lookAwaying = False
                    words = ""
                    for word in self.words:
                        words += (word + " ")
                    self.sendMessage("words " + words)
        elif self.wording:
            if self.name == self.names[self.turn]:
                if event.x < 334 and (200 < event.y < 400):
                    self.word = self.words[0]
                elif 334 < event.x <= 666 and (200 < event.y < 400):
                    self.word = self.words[1]
                elif event. x > 667 and (200 < event.y < 400):
                    self.word = self.words[2]
                if self.word != "":
                    self.playing = True
                    self.wording = False
                    self.sendMessage("word " + self.word)
                    self.sendMessage("time " + str(60))
            else:
                pass
        elif self.playing:
            if self.gameOver:
                pass
            elif not self.winning:
                if 350 < event.x < 375:
                    if 300 < event.y < 425:
                        if self.chatIndex > 0:
                            self.chatIndex -= 1
                    elif 425 < event.y < 550:
                        if (len(self.chatlog) >= 11 and 
                            self.chatIndex + 11 < len(self.chatlog)):
                            self.chatIndex += 1
                elif self.name == self.names[self.turn]:
                    if ((self.drawSpace[0] <= event.x <= self.drawSpace[2]) and
                            (self.drawSpace[1] <= event.y <= self.drawSpace[3])):
                        if self.tool3:
                            self.recursiveBrush(round((event.x-400)/10), 
                                round((event.y-100)/10), self.thicknesses[self.tool2])
                            temp = sum(self.board, [])
                            temp2 = []
                            for e in temp:
                                temp2.append(str(e))
                            board = " ".join(temp2)
                            self.sendMessage("board " + board)
                            
                        else:
                            self.lines.append(0)
                            self.sendMessage("lineStop")
                    elif 500 < event.y < 550:
                        for i in range(7):
                            if 400+i*50 < event.x < 450+i*50:
                                if i == 6:
                                    self.tool3 = not self.tool3
                                    self.board = [([5]*55) for row in range(40)]
                                    self.lines = []
                                    self.sendMessage("tool3")
                                else:
                                    self.tool = i
                                    self.color = self.colors[i]
                                    self.sendMessage("tool " + str(i))
                        for i in range(6):
                            if 800+i*25 < event.x < 850+i*25:
                                self.tool2 = i
                                self.sendMessage("tool2 " + str(i))

    #cont. function called when mouse is dragged on draw board
    def mouseDragged(self, event):
        if self.playing:
            if self.gameOver:
                pass
            elif self.name == self.names[self.turn]:
                if ((self.drawSpace[0] <= event.x <= self.drawSpace[2]) and
                (self.drawSpace[1] <= event.y <= self.drawSpace[3])):
                    if self.tool3:
                        self.recursiveBrush(round((event.x-400)/10), 
                            round((event.y-100)/10), self.thicknesses[self.tool2])
                        temp = sum(self.board, [])
                        temp2 = []
                        for e in temp:
                            temp2.append(str(e))
                        board = " ".join(temp2)
                        self.sendMessage("board " + board)
                    else:
                        self.lines.append((event.x,event.y,self.tool2,self.color))
                        self.sendMessage("lines " + str(event.x) + " " + str(event.y) + " " + str(self.tool2) + " " + self.color)
                elif 500 < event.y < 550:
                    for i in range(6):
                        if 800+i*25 < event.x < 850+i*25:
                            self.tool2 = i
                            self.sendMessage("tool2 " + str(i))

    #cont. function called when key is pressed at certain stages of game
    def keyPressed(self, event):
        if self.gameOver:
            if event.key == "Tab":
                self.changeLeaderboard()
                self.restart()
        elif self.winning:
            if event.key == "Tab":
                self.round += 1
                self.playing = False
                self.roundRestart()
                self.changeTurn()
        else:
            if self.playing:
                if (len(event.key) == 1) and (len(self.chatline) < 18):
                    self.chatline += (event.key)
                elif event.key == "Space":
                    self.chatline += " "
                elif event.key == "Delete":
                    if len(self.chatline) > 0:
                        self.chatline = self.chatline[:-1]
                elif event.key == "Enter":
                    if self.chatline.upper() == self.word and (self.name != self.names[self.turn]) and (not self.tempWinning):
                        self.tempWinning = True
                        self.wins += 1
                        if self.wins == len(self.names)-1:
                            self.winning = True
                            self.sendMessage("winning")
                        if int(self.roundTime) >= 45:
                            if self.diff < 3:
                                self.diff += 1
                        elif int(self.roundTime) >= 25:
                            pass
                        else:
                            if self.diff > 1:
                                self.diff -= 1
                        self.sendMessage("diff " + str(self.diff))
                        self.sendMessage("wins")
                        self.chatlog.append(self.name + " guessed the word!")
                        if len(self.chatlog) >= 12:
                            self.chatIndex = len(self.chatlog)-11
                        self.chatline = ""
                        self.roundScore()
                        self.sendMessage("score " + str(self.score[0]) + " " + str(self.score[1]) + " " + str(self.score[2]) + " " + str(self.score[3]))
                    elif self.chatline == "":
                        pass
                    else:
                        self.chatlog.append(self.name + ": " + self.chatline)
                        if len(self.chatlog) >= 12:
                            self.chatIndex = len(self.chatlog)-11
                        self.sendMessage("chatSend " + self.chatline)
                        self.chatline = ""
                        

    #VIEW FUNCTIONS-------------------------------------------------------------

    #helper view function that draws background at all times
    def drawBackground(self, canvas):
        canvas.create_rectangle(0, 0, self.width, self.height, fill='deep sky blue')
        #pencil gif SOURCE: https://gph.is/st/Y9xlJ8M
        canvas.create_image(70, 70, image=ImageTk.PhotoImage(self.image))
        canvas.create_text(248, 70, text='Draw Something!', 
            font=('Comic Sans MS', 30, 'bold'), fill='white')
        canvas.create_text(252, 70, text='Draw Something!', 
            font=('Comic Sans MS', 30, 'bold'), fill='white')
        canvas.create_text(250, 68, text='Draw Something!', 
            font=('Comic Sans MS', 30, 'bold'), fill='white')
        canvas.create_text(250, 72, text='Draw Something!', 
            font=('Comic Sans MS', 30, 'bold'), fill='white')
        canvas.create_text(250, 70, text='Draw Something!', 
            font=('Comic Sans MS', 30, 'bold'))
        for i in range(len(self.names)):
            if i == self.turn:
                canvas.create_text(200,200+20*i, text= self.names[i] + " connected! (drawer)")
            else:
                canvas.create_text(200,200+20*i, text= self.names[i] + " connected!")

    #helper view function that draws leaderboard on start page
    def drawLeaderboard(self, canvas):
        canvas.create_rectangle(300,100,700,500, fill="white", width=3)
        canvas.create_text(self.width/2, 150, text= "Leaderboard:", 
                font=("Comic Sans MS", 40, "bold"))
        for i in range(len(leaderboard())):
            canvas.create_text(self.width/2, 220+50*i, text=leaderboard()[i],
                font=("Comic Sans MS", 20))

    #helper view function that draws start page
    def drawStartPage(self, canvas):
        self.drawLeaderboard(canvas)
        canvas.create_rectangle(self.playButton, fill="white",
                width=3)
        canvas.create_text(600, 550, text="Play",
                font=('Comic Sans MS', 25, 'bold'))
        canvas.create_rectangle(self.wordButton, fill="white",
                width=3)
        canvas.create_text(400, 550, text="Words",
                font=('Comic Sans MS', 25, 'bold'))
    
    #helper view function that draws page explaining how to add custom words
    def drawWordBankPage(self, canvas):
        canvas.create_text(self.width/2, self.height/2, font=("Comic Sans MS", 20), 
                text="If you want to use your own custom words,")
        canvas.create_text(self.width/2, self.height/2+30, font=("Comic Sans MS", 20), 
                text="make a .txt file with words separated by commas")
        canvas.create_text(self.width/2, self.height/2+60, font=("Comic Sans MS", 20), 
                text="and drop the file in the same folder as the game!")
        canvas.create_rectangle(self.backButton, fill="white",
                width=3)
        canvas.create_text(self.width/2, 550, text="Back",
                font=('Comic Sans MS', 25, 'bold'))
    
    #helper view function that draws word selection page
    def drawWordPage(self, canvas):
        if self.name == self.names[self.turn]:
            canvas.create_text(200, 130, text=("Time Left: " + str(int(self.wordTime))),
                    font=("Comic Sans MS", 20))
            canvas.create_text(self.width/2, self.height/2-100, text="Choose a word!",
                    font=("Comic Sans MS", 30))
            canvas.create_text(167,self.height/2, text=self.words[0],
                    font=("Comic Sans MS", 40, "bold"))
            canvas.create_text(500,self.height/2, text=self.words[1],
                    font=("Comic Sans MS", 40, "bold"))
            canvas.create_text(833,self.height/2, text=self.words[2],
                    font=("Comic Sans MS", 40, "bold"))
            canvas.create_text(self.width/2, 500, 
                    text="failing to choose in time will default to the middle word.",
                    font=("Comic Sans MS", 20))
            if self.diff == 1:
                canvas.create_text(self.width/2, 450, text="Difficulty: Easy",
                    font=("Comic Sans MS", 20))
            elif self.diff == 2:
                canvas.create_text(self.width/2, 450, text="Difficulty: Medium",
                    font=("Comic Sans MS", 20))
            else:
                canvas.create_text(self.width/2, 450, text="Difficulty: Hard!",
                    font=("Comic Sans MS", 20))
        else:
            canvas.create_text(200, 130, text=("Time Left: " + str(int(self.wordTime))),
                    font=("Comic Sans MS", 20))
            canvas.create_text(self.width/2, 500, 
                    text="You are the guesser! Please wait while the drawer picks a word.",
                    font=("Comic Sans MS", 20))

    #helper view function that draws page warning players to look away
    def drawLookAwayPage(self, canvas):
        if self.name == self.names[self.turn]:
            canvas.create_text(self.width/2, self.height/2, 
                    text= "Press Ready when everyone has reached this page.",
                    font=("Comic Sans MS", 40))
            canvas.create_rectangle(self.backButton, fill="white",
                    width=3)
            canvas.create_text(self.width/2, 550, text="Ready",
                    font=('Comic Sans MS', 25, 'bold'))
        else:
            canvas.create_text(self.width/2, self.height/2, 
                    text= "Waiting for drawer to start...",
                    font=("Comic Sans MS", 40))
    
    #helper view function that draws main, drawing page
    def drawPlayPage(self, canvas):
        
        canvas.create_rectangle(self.drawSpace, fill="white", width=3)
        canvas.create_text(625,50, text=hiddenWord(self.word), 
                font=("Comic Sans MS", 40, "bold"))
        canvas.create_text(200, 130, text=("Time Left: " + str(int(self.roundTime))),
                font=("Comic Sans MS", 20))
        canvas.create_rectangle(self.chatSpace, fill="white", width=3)
        for i in range(2):
            canvas.create_rectangle(350,300+125*i,375,425+125*i, fill="white", width=3)
        canvas.create_text(363,363, text="/\\", font=("Ariel",10))
        canvas.create_text(363,488, text="\\/", font=("Ariel", 10))
        canvas.create_line(50,530,350,530)
        canvas.create_text(200, 540, text=self.name + ": " + self.chatline,
                font=("Courier New", 15))
        for i in range(len(self.chatlog)):
            if i >= 11:
                pass
            else:
                canvas.create_text(200,310+i*20, text= self.chatlog[i+self.chatIndex], 
                    font=("Courier New", 15))
        if self.name == self.names[self.turn]:
            canvas.create_rectangle(self.toolSpace, fill="white", width=3)
            canvas.create_rectangle(400+50*self.tool,500,450+50*self.tool,550,
                    fill="grey", width=3)
            canvas.create_line(810,525,940,525, width=5)
            canvas.create_rectangle(800+25*self.tool2,515,820+25*self.tool2,535,
                    fill="black")
            canvas.create_oval(405,505,445,545, fill="black")
            canvas.create_oval(455,505,495,545, fill="blue")
            canvas.create_oval(505,505,545,545, fill="green")
            canvas.create_oval(555,505,595,545, fill="yellow")
            canvas.create_oval(605,505,645,545, fill="red")
            canvas.create_rectangle(665,510,685,540, fill="pink", width=2)
            canvas.create_text(725,525, text="MODE", font=("Comic Sans MS", 15, "bold"))
            canvas.create_oval(770-3*self.tool2,520-3*self.tool2,
                    780+3*self.tool2,530+3*self.tool2, fill="black")
    
    #helper view function that draws brush for floodfill recursion mode
    def drawBrush(self, canvas):
        for row in range(40):
            for col in range(55):
                canvas.create_rectangle((10*col+400,10*row+100)*2, width=10, 
                    outline=self.colors[self.board[row][col]])
    
    #helper view function that draws brush for line mode
    def drawBrush2(self, canvas):
        for i in range(len(self.lines)-1):
            if (self.lines[i+1] == 0) or (self.lines[i] == 0):
                pass
            else:
                canvas.create_line(self.lines[i][0], self.lines[i][1],
                    self.lines[i+1][0], self.lines[i+1][1], width=5*self.lines[i][2],
                    fill=self.lines[i][3])

    #helper view function that draws game over popup
    def drawGameOver(self, canvas):
        canvas.create_rectangle(200,100,800,500, fill="white", width=3)
        canvas.create_text(self.width/2, 200, text="Game Over at Round " + str(self.round), 
                font=("Comic Sans MS", 30, "bold"))
        canvas.create_text(self.width/2, 230, text="The word was "
                + self.word + ".", font=("Comic Sans MS", 20, "bold"))
        if len(self.names) == 3:
            canvas.create_text(self.width/2, 290, text= "Score: " + 
                self.names[2] + ": " + str(self.score[2]), font=("Comic Sans MS", 20, "bold"))
        elif len(self.names) == 4:
            canvas.create_text(self.width/2, 290, text= "Score: " + 
                self.names[2] + ": " + str(self.score[2]) + ", " + 
                self.names[3] + ": " + str(self.score[3]), font=("Comic Sans MS", 20, "bold"))
        canvas.create_text(self.width/2, 260, text= "Score: " + 
                self.names[0] + ": " + str(self.score[0]) + ", " + 
                self.names[1] + ": " + str(self.score[1]), font=("Comic Sans MS", 20, "bold"))
        canvas.create_text(self.width/2, 350, text="Press the Tab Key to continue",
                font=("Comic Sans MS", 20, "bold"))
    
    #helper view function that draws round win pop up
    def drawWin(self, canvas):
        canvas.create_rectangle(200,100,800,500, fill="white", width=3)
        canvas.create_text(self.width/2, 200, text="Passed Round " + str(self.round) + "!", 
                font=("Comic Sans MS", 30, "bold"))
        canvas.create_text(self.width/2, 230, text="The word was "
                + self.word + ".", font=("Comic Sans MS", 20, "bold"))
        if len(self.names) == 3:
            canvas.create_text(self.width/2, 290, text= "Current Score: " + 
                self.names[2] + ": " + str(self.score[2]), font=("Comic Sans MS", 20, "bold"))
        elif len(self.names) == 4:
            canvas.create_text(self.width/2, 290, text= "Current Score: " + 
                self.names[2] + ": " + str(self.score[2]) + ", " + 
                self.names[3] + ": " + str(self.score[3]), font=("Comic Sans MS", 20, "bold"))
        canvas.create_text(self.width/2, 260, text= "Current Score: " + 
                self.names[0] + ": " + str(self.score[0]) + ", " + 
                self.names[1] + ": " + str(self.score[1]), font=("Comic Sans MS", 20, "bold"))
        canvas.create_text(self.width/2, 350, text="Press the Tab Key to move to the next round!",
                font=("Comic Sans MS", 20, "bold"))

    #view function that draws everythang
    def redrawAll(self, canvas):
        self.drawBackground(canvas)
        if self.starting:
            self.drawStartPage(canvas)
        elif self.wordBanking:
            self.drawWordBankPage(canvas)
        elif self.lookAwaying:
            self.drawLookAwayPage(canvas)
        elif self.wording:
            self.drawWordPage(canvas)
        elif self.playing:
            self.drawPlayPage(canvas)
            if self.tool3:
                self.drawBrush(canvas)
            else:
                self.drawBrush2(canvas)
            if self.gameOver:
                self.drawGameOver(canvas)
            elif self.winning:
                self.drawWin(canvas)
        
MyApp(title="Draw Something!", width=1000, height=600)
