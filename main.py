from tkinter import *
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import os, os.path
import random
import time

RESIZE_RATIO = 4
canvas_width = 800
canvas_height = 800

SUITS = ("Spades", "Hearts", "Clubs", "Diamonds")
NUMBER_OF_CARDS = 52
SUIT_LENGTH = 13  # amount of cards each suit contains
BUST_LIMIT = 21
MULT_TAB = "\t"*1

FACE_CARD_VALUE = 10
ACE_MAX_VALUE = 11
ACE_MIN_VALUE = 1

START_AMOUNT_CARDS = 2
STARTING_MONEY = 1000
MIN_CARDS_IN_DECK = 15  # if deck has <= 15 cards, deck resets

DEFAULT_BET = 25

DEALER_HIT_LIMIT = 17
DEALER_DELAY = 0.75

PLAYER_CARD_Y = 550
DEALER_CARD_Y = 0

master = Tk()
master.resizable(False, False)
canvas = Canvas(master,
           width=canvas_width,
           height=canvas_height,
            bd=0,highlightthickness=0, relief='ridge')
canvas.pack()

class Card:
    def __init__(self, number, suit, frontImage, backImage, orientation="back"):
        self.__number = number
        self.__suit = suit

        self.__frontImage = frontImage
        self.__backImage = backImage
        self.__orientation = "back"
        self.__xPos = 600
        self.__yPos = 275

        refLabelBack = Label(image=backImage)
        refLabelBack.image = backImage

        refLabelFront = Label(image=frontImage)
        refLabelFront.image = frontImage

        if type(number) == int:
            self.__value = number
        else:
            if number == "J" or number == "Q" or number == "K":
                self.__value = FACE_CARD_VALUE
            else:
                self.__value = ACE_MAX_VALUE

    def __str__(self):
        return (str(self.__number) + " of " + self.__suit)

    def changeValue(self, newValue):
        self.__value = newValue

    def getValue(self):
        return self.__value

    def createImage(self, image):
        self.__sprite = canvas.create_image(self.__xPos, self.__yPos, anchor=NW, image=image)

    def move(self, xPos, side, speed="slow"):
        if self.__orientation == "back":
            self.createImage(self.__backImage)
        elif self.__orientation == "front":
            self.createImage(self.__frontImage)
        sprite = self.__sprite

        if speed == "slow":
            rate = 100
        elif speed == "medium":
            rate = 50
        elif speed == "fast":
            rate = 10

        if side == "player":
            yPos = PLAYER_CARD_Y
        else:
            yPos = DEALER_CARD_Y

        xChange = xPos - self.__xPos
        yChange = yPos - self.__yPos

        for posChange in range(rate):
            canvas.move(sprite, xChange/rate, yChange/rate)
            self.__xPos += xChange/rate
            self.__yPos += yChange/rate
            canvas.update()

    def flip(self, side=False):
        canvas.delete(self.__sprite)
        if side == False:
            if self.__orientation == "back":
                self.__orientation = "front"
                self.createImage(self.__frontImage)
            elif self.__orientation == "front":
                self.__orientation = "back"
                self.createImage(self.__backImage)
        else:
            self.__orientation = side
            if side == "front":
                self.createImage(self.__frontImage)
            elif side == "back":
                self.createImage(self.__backImage)

    def deleteCard(self):
        canvas.delete(self.__sprite)

class Deck:
    def __init__(self):
        self.resetDeck()
        self.__dealerHand = []
        self.__dealerValue = 0
        self.__cardPos = 0
        canvas.create_image(600, 275, anchor=NW, image=deckPhoto)

    def __str__(self):
        return str(self.getDeck())

    def resetDeck(self):
        cardTypes = []
        for numberedCards in range(2,11):
            cardTypes.append(numberedCards)
        cardTypes.append("J")
        cardTypes.append("Q")
        cardTypes.append("K")
        cardTypes.append("A")

        deckList = []

        for suitNumber in range(0, len(SUITS)):
            cardSuit = SUITS[suitNumber]
            for cardNumber in range(0, SUIT_LENGTH):
                cardName = cardTypes[cardNumber]
                cardPhoto = findFile(cardName, cardSuit)

                deckList.append(Card(cardName, cardSuit, cardPhoto, backCardPhoto))
        #rigList = [("K", "Clubs"), ("3", "Clubs"), ("8", "Clubs"), ("3", "Diamonds"), ("A", "Clubs"), ("2", "Hearts"), ("2", "Spades"), ("8", "Spades")]
        #deckOrder = 0
        #for card in rigList:
        #    cardPhoto = findFile(card[0], card[1])
        #    deckList[deckOrder] = Card(card[0], card[1], cardPhoto, backCardPhoto)
        #    deckOrder += 1

        #deckList[0] = (Card("K", "Clubs"))
        #deckList[1] = (Card("3", "Clubs"))
        #deckList[2] = (Card("8", "Clubs"))
        #deckList[3] = (Card("3", "Diamonds"))
        #deckList[4] = (Card("A", "Clubs"))
        #deckList[5] = (Card("2", "Hearts"))
        #deckList[3] = (Card("2", "Spades"))
        self.__deckList = deckList
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.__deckList)

    def drawCard(self):
        return self.__deckList.pop(0)

    def deal(self, player):
        self.__cardPos = 0
        for startingHandLength in range(START_AMOUNT_CARDS):
            player.takeCard(self.drawCard())
            self.dealDealer()

    def dealPlayer(self, player):
        player.takeCard(self.drawCard())

    def dealDealer(self):
        newCard = self.drawCard()
        self.__dealerHand.append(newCard)
        newCard.move(self.__cardPos, "dealer")
        self.__cardPos += 100
        if self.__dealerHand.index(newCard) != 1:
            newCard.flip()

    def newHand(self, player):
        for card in self.__dealerHand:
            card.deleteCard()

        self.__dealerHand = []
        player.newHand()
        if len(self.__deckList) < MIN_CARDS_IN_DECK:
            self.resetDeck()
            #print ("\nReshuffled.\n")

    def getDealerHand(self, returnList = False):
        if returnList == True:
            dealerHandList = []
            for card in self.__dealerHand:
                dealerHandList.append(str(card))
            return dealerHandList
        else:
            return self.__dealerHand

    def getDeck(self):
        stringDeckList = []
        for card in self.__deckList:
            stringDeckList.append(str(card))
        return stringDeckList

    def getValue(self):
        value = 0
        for card in self.__dealerHand:
            value += card.getValue()

        if value > BUST_LIMIT:
            for card in self.__dealerHand:
                if card.getValue() == ACE_MAX_VALUE:
                    card.changeValue(ACE_MIN_VALUE)
                    value -= (ACE_MAX_VALUE - ACE_MIN_VALUE)
                if value <= BUST_LIMIT:
                    break

        return value


class Player:
    def __init__(self):
        self.__playerName = simpledialog.askstring("Welcome to Blackjack!", "Get as close to 21 as you can without busting.\nMinimum ante is $25. Dollar amounts only. \nGood luck! \n\nWhat is your first name?", parent=master).strip()
        self.__playerName
        self.__money = STARTING_MONEY
        self.__highscore = STARTING_MONEY
        self.__bet = 0
        self.__hand = []

        betButton.config(state=NORMAL)
        betEntry.config(state=NORMAL)

        fileName = "highscores.txt"
        self.__fileName = fileName
        scores = None

        try:
            scores = open(fileName, 'r')
            self.__scoresList = scores.readlines()
            for elem in range(0, len(self.__scoresList)):
                self.__scoresList[elem] = self.__scoresList[elem].strip("\n")
            if not self.__playerName in self.__scoresList:
                self.__scoresList.append(self.__playerName)
                self.__scoresList.append(str(self.__money))
            #print(self.__scoresList)
        except:
            scores = open(fileName, 'w')
            self.__scoresList = []
            self.__scoresList.append(self.__playerName)
            self.__scoresList.append(str(self.__money))

        
        scores.close()

        self.updateHighscore()
        self.__cardPos = 0

    def __str__(self):
        return (self.__playerName + " has $" + str(self.__money))

    def ante(self, bet, doubleDown=False):
        if not doubleDown:
            self.__bet = bet
            self.__money -= bet
        else:
            self.__money -= self.__bet
            self.__bet = self.__bet*2

        self.updateHighscore()

    def takeCard(self, card):
        self.__hand.append(card)
        card.move(self.__cardPos, "player")
        self.__cardPos += 100
        card.flip("front")

    def setMoney(self, money):
        self.__money = money

    def getHand(self, returnList = False):
        if returnList == True:
            playerHandList = []
            for card in self.__hand:
                playerHandList.append(str(card))
            return playerHandList
        else:
            return self.__hand

    def handOver(self, result):
        hitButton.config(state=DISABLED)
        stayButton.config(state=DISABLED)
        if result == "win":
            self.__money += self.__bet*2
        elif result == "push":
            self.__money += self.__bet
        elif result == "player blackjack":
            self.__money += self.__bet*2.5
            self.__money = round(self.__money)

        self.updateHighscore()


    def newHand(self):
        self.__cardPos = 0
        for card in self.__hand:
            card.deleteCard()
        self.__hand = []


    def getAnte(self):
        return str(self.__bet)

    def getName(self):
        return str(self.__playerName)

    def getValue(self):
        value = 0
        for card in self.__hand:
            value += card.getValue()

        if value > BUST_LIMIT:
            for card in self.__hand:
                if card.getValue() == ACE_MAX_VALUE:
                    card.changeValue(ACE_MIN_VALUE)
                    value -= (ACE_MAX_VALUE - ACE_MIN_VALUE)
                if value <= BUST_LIMIT:
                    break

        return value

    def getMoney(self):
        return self.__money

    def updateHighscore(self):
        scores = open(self.__fileName, 'w')
        self.__maxScore = 0
        for elem in self.__scoresList:
            try:
                if elem == self.__playerName:
                    if self.__money > int(self.__scoresList[self.__scoresList.index(self.__playerName) + 1]):
                        self.__scoresList[self.__scoresList.index(self.__playerName) + 1] = self.__money
                        self.__highscore = self.__money
                    else:
                        self.__highscore = int(self.__scoresList[self.__scoresList.index(self.__playerName) + 1])

            except ValueError:
                continue

        for elem in self.__scoresList:
            try:
                if int(elem) > self.__maxScore:
                    self.__maxScore = int(elem)
            except ValueError:
                continue
            self.__scoresList[self.__scoresList.index(elem)] = str(elem)

        scores.write("\n".join(self.__scoresList))
        scores.close()


    def getTitle(self):
        return self.__playerName.capitalize() + "'s hiscore: " + str(self.__highscore) + "\t\tBest score: " + str(self.__maxScore)


def gameState(turn, doubleDown=False):
    dealerHand = deck.getDealerHand()
    dealerHandList = deck.getDealerHand(returnList=True)
    dealerValue = deck.getValue()


    playerName = player.getName()
    playerHand = player.getHand()
    playerHandList = player.getHand(returnList=True)
    playerValue = player.getValue()

    blackjackState = "none"
    bust = False

    if turn == "player":
        if playerValue > BUST_LIMIT:
            bust = True

        if len(playerHand) == START_AMOUNT_CARDS and playerValue == BUST_LIMIT:
            dealerHand[1].flip("front")
            blackjackState = "player"

        if len(dealerHand) == START_AMOUNT_CARDS and dealerValue == BUST_LIMIT:
            dealerHand[1].flip("front")
            if blackjackState != "player":
                blackjackState = "dealer"
                displayResult("Player loses.")
            else:
                blackjackState = "push"
                player.handOver("push")
                displayResult("Push.")

        if blackjackState == "player":
            player.handOver("player blackjack")
            displayResult("Blackjack!")

    if turn == "dealer":
        dealerChoice = False
        if dealerValue < DEALER_HIT_LIMIT:
            dealerChoice = "hit"
        elif dealerValue <= BUST_LIMIT:
            if dealerValue > playerValue:
                dealerChoice = "wins."
            elif dealerValue == playerValue:
                dealerChoice = "pushes."
            else:
                for card in dealerHand:
                    if card.getValue() == ACE_MAX_VALUE:
                        card.changeValue(ACE_MIN_VALUE)
                        dealerValue = deck.getValue()
                    if dealerValue < DEALER_HIT_LIMIT:
                        dealerChoice = "hit"
                        break
                if dealerValue >= DEALER_HIT_LIMIT:
                    if dealerValue == playerValue:
                        dealerChoice = "pushes."
                    else:
                        dealerChoice = "loses."
        else:
            dealerChoice = "loses."

    if turn == "player":
        if bust:
            displayResult("Player busts.")
        else:
            if not doubleDown:
                if blackjackState == "none":
                    hitButton.config(state=NORMAL)
                    stayButton.config(state=NORMAL)
                    if len(playerHandList) == 2 and int(player.getAnte()) <= int(player.getMoney()):
                        doubleDownButton.config(state=NORMAL)
            else:
                stay()

    if turn == "dealer":
        if dealerChoice == "hit":
            deck.dealDealer()
            gameState(turn="dealer")
        elif dealerChoice == "wins.":
            displayResult("Dealer wins.")
        elif dealerChoice == "loses.":
            player.handOver("win")
            displayResult("Player wins.")
        elif dealerChoice == "pushes.":
            player.handOver("push")
            displayResult("Push.")

def displayResult(displayText):
    global resultText, nextHandButton
    resultText = canvas.create_text(400, 400, text = displayText, fill="white", font=("Purisa", 24))
    nextHandButton = Button(canvas, width=5, height=2, text="Okay", command=reset, state=NORMAL)
    nextHandButton.place(x=420, y=440, anchor=NE)
    hitButton.config(state=DISABLED)
    stayButton.config(state=DISABLED)


# Takes card number and suit and returns file name for card's image
def findFile(number, suit):
    fileName = str(number) + str(suit).lower() + ".png"
    for im in cardImages:
        if fileName in im.filename:
            frontCardImage = im.resize((round(729/RESIZE_RATIO), round(1024/RESIZE_RATIO)), Image.ANTIALIAS)
            frontCardPhoto = ImageTk.PhotoImage(frontCardImage)
            return frontCardPhoto

# Converts image file into photo object
def photoConvert(file,resize=True):
    image = Image.open(file)
    if resize:
        image = image.resize((round(729/RESIZE_RATIO), round(1024/RESIZE_RATIO)), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(image)

    return photo

def reset():
    global overText, newGameButton
    #print (player.getMoney())
    canvas.delete(resultText)
    nextHandButton.destroy()
    hitButton.config(state=DISABLED)
    stayButton.config(state=DISABLED)
    doubleDownButton.config(state=DISABLED)
    canvas.itemconfigure(moneyText, text="Money: $" + str(player.getMoney()))
    master.title(player.getTitle())
    if int(player.getMoney()) >= 25:
        betButton.config(state=NORMAL)
        betEntry.config(state=NORMAL)
        player.newHand()
        deck.newHand(player)
    else:
        overText = canvas.create_text(400, 400, text = "Game over.", fill="white", font=("Purisa", 24))
        newGameButton = Button(canvas, width=5, height=2, text="Restart", command=newGame, state=NORMAL)
        newGameButton.place(x=420, y=440, anchor=NE)

def newGame():
    canvas.delete(overText)
    newGameButton.destroy()
    betButton.config(state=NORMAL)
    betEntry.config(state=NORMAL)
    deck.resetDeck()
    player.setMoney(STARTING_MONEY)
    canvas.itemconfigure(moneyText, text="Money: $" + str(player.getMoney()))
    player.newHand()
    deck.newHand(player)


def newHand():
    #print (player.getMoney())
    betButton.config(state=DISABLED)
    betEntry.config(state=DISABLED)
    deck.deal(player)
    gameState("player")

def bet():
    global money
    try:
        bet = int(betEntry.get())
    except ValueError:
        messagebox.showerror("Error", "Bet must be integer.")

    if bet < 25:
        messagebox.showerror("Error", "Minimum bet is $25.")
    elif bet > int(player.getMoney()):
        messagebox.showerror("Error", "Cannot bet more than you have.")
    else:
        player.ante(bet)
        newMoney = player.getMoney()
        money.set(str(newMoney))
        canvas.itemconfigure(moneyText, text="Money: $" + str(money.get()))

        newHand()

def hit():
    hitButton.configure(state=DISABLED)
    stayButton.configure(state=DISABLED)
    doubleDownButton.configure(state=DISABLED)
    deck.dealPlayer(player)
    gameState("player")

def stay():
    hitButton.configure(state=DISABLED)
    stayButton.configure(state=DISABLED)
    doubleDownButton.configure(state=DISABLED)
    deckList = deck.getDealerHand()
    wildCard = deckList[1]
    wildCard.flip()
    gameState("dealer")

def doubleDown():
    doubleDownButton.configure(state=DISABLED)
    hitButton.configure(state=DISABLED)
    stayButton.configure(state=DISABLED)

    player.ante(0, doubleDown=True)
    canvas.itemconfigure(moneyText, text="Money: $" + str(player.getMoney()))

    deck.dealPlayer(player)
    gameState("player", doubleDown=True)

def quitGame():
    master.destroy()
    raise SystemExit(0)

def donothing():
    pass

def returnButton(event):
    master.grab_set()
    if betButton.cget('state') == "normal":
        bet()
    elif hitButton.cget('state') == "normal":
        hit()
    elif nextHandButton.winfo_exists() == 1:
        reset()
    elif newGameButton.winfo_exists() == 1:
        newGame()

def spaceButton(event):
    master.grab_set()
    if stayButton.cget('state') == "normal":
        stay()

def downButton(event):
    master.grab_set()
    if betButton.cget('state') == "normal":
        try:
            entryText = int(betEntry.get())
            if entryText > 250:
                entryText -= 250
                if entryText > int(player.getMoney()):
                    entryText = int(player.getMoney())
            else:
                entryText = 0
            betEntry.delete(0, END)
            betEntry.insert(0, str(entryText))
        except ValueError:
            return

    elif doubleDownButton.cget('state') == "normal":
        doubleDown()

def upButton(event):
    master.grab_set()
    if betButton.cget('state') == "normal":
        try:
            entryText = int(betEntry.get())
            if entryText + 250 < int(player.getMoney()):
                entryText += 250
            else:
                entryText = int(player.getMoney())
            betEntry.delete(0, END)
            betEntry.insert(0, str(entryText))
        except ValueError:
            return

def shiftButton(event):
    master.grab_set()
    if doubleDownButton.cget('state') == "normal":
        doubleDown()

def escapeButton(event):
    master.grab_set()
    quitGame()

# Imports card images
cardImages = []
path = "./images/cardFronts"
valid_images = [".png"]

for f in os.listdir(path):
    ext = os.path.splitext(f)[1]
    if ext.lower() not in valid_images:
        continue
    cardImages.append(Image.open(os.path.join(path,f)))

# filenames for table, card back and deck images
tablePhoto = photoConvert("./images/table.png",resize=False)
backCardPhoto = photoConvert("./images/cardBacks/pittCardBack.png")
deckPhoto = photoConvert("./images/cardBacks/deck.png")

canvas.create_image(-5,-5,anchor=NW,image=tablePhoto)
canvas.create_image(600,275,anchor=NW, image=deckPhoto)

master.protocol('WM_DELETE_WINDOW',donothing)

money = StringVar()
money.set('1000')
moneyText = canvas.create_text(690,670,text="Money: $" + str(money.get()), fill="white", font=("Purisa", 24))

betButton = Button(canvas, width=10, height=2, text="Bet", command=bet, state=DISABLED)
betButton.place(x=740, y=700, anchor=NE)

hitButton = Button(canvas, width=6, height=2, text="Hit", command=hit, state=DISABLED)
hitButton.place(x=690, y=540, anchor=NE)

stayButton = Button(canvas, width=6, height=2, text="Stay", command=stay, state=DISABLED)
stayButton.place(x=749, y=540, anchor=NE)

doubleDownButton = Button(canvas, width=11, height=2, text="Double Down", command=doubleDown, state=DISABLED)
doubleDownButton.place(x=743,y=577,anchor=NE)

betText = StringVar()
betText.set("500")
betEntry = Entry(canvas, text = "Type here: ", textvariable = betText, state=DISABLED)
betEntry.place(x=740,y=735,anchor=NE,width=94)

quitButton = Button(canvas, width=5, height=2, text="Quit", command=quitGame, state=NORMAL)
quitButton.place(x=800, y=0, anchor=NE)

nextHandButton = Button(canvas, width=5, height=2, text="Okay", command=reset, state=NORMAL)
nextHandButton.destroy()

newGameButton = Button(canvas, width=5, height=2, text="Restart", command=newGame, state=NORMAL)
newGameButton.destroy()

master.bind("<Return>", returnButton)
master.bind("<space>", spaceButton)
master.bind("<Up>", upButton)
master.bind("<Down>", downButton)
master.bind("<Escape>", escapeButton)
master.bind("<Shift_L>", shiftButton)

top = Toplevel()


player = Player()
deck = Deck()
master.title(player.getTitle())

mainloop()
