class Sevens:
    def __init__(self, noPlayers):
        self.suits = ("C", "D", "H", "S")
        self.ranks = ("A", "2", "3", "4", "5", "6", "7","8", "9", "10", "J", "Q", "K")
        self.deck = []
        self.board = []
        self.iCards = {}
        self.noPlayers = noPlayers


        for i in range(len(self.suits)):
            column = []
            for j in range(len(self.ranks)):
                card = []
                card.append[ranks[j]]
                card.append[ranks[i]]
                self.deck.append(card)
                column.append(None)
                self.iCards[card] = Image.open("./{}.png".format(card))
            self.board.append(column)

