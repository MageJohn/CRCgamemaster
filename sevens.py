class Sevens:
    def __init__(self):
        self.suits = ("C", "D", "H", "S")
        self.ranks = ("A", "2", "3", "4", "5", "6", "7","8", "9", "10", "J", "Q", "K")
        self.deck = []
        self.board = []
        self.iCards = {}
        for i in range(4):
            column = []
            for j in range(13):
                card = self.ranks[j] + self.suits[i]
                self.append(card)
                column.append(None)
                self.iCards[card] = Image.open('./' + card + '.png')
            self.board.append(column)
         
