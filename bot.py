import discord
from discord.ext import commands
import getSave
import ticTacToe
from PIL import Image

# TO DO:
# add turn as an attribute of gamerooms.txt - Done!

TOKEN="token.txt"

NUM_GAMEROOMS = 4

description = '''CRC Gamemaster Bot'''
bot = commands.Bot(command_prefix='$', description=description)
GAMES = {"tic-tac-toe": (2, 2, ticTacToe.TicTacToe)} # format: {gameName: (minPlayers, maxPlayers, gameObject) ...}
serverName = 'CRC Buddies'

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    # extra commands go here

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def rooms():
    """Lists players in each gameroom and the game"""
    rooms = getSave.get("gamerooms.txt")
    anyGames = False
    response = "The games in progress are:\n\n"
    for i in range(len(rooms)):
        if len(rooms[i]) > 1:
            contents = "gameroom-"
            contents += str(i+1)
            contents += ": "
            for j in range(len(rooms[i])-2): 
                contents += rooms[i][j+2]
                if j < (len(rooms[i]) - 4):
                    contents += ", "
                elif j == (len(rooms[i]) - 4):
                    contents += " and " 
            contents += " playing "
            contents += rooms[i][0]
            response += contents
            response += "\n\n"
            anyGames = True
    if anyGames:
        await bot.say(response)
    else:
        await bot.say("There are no games currently in progress.")

@bot.command()
async def guide(game : str):
    """Outputs guide to game"""
    if game in knownGames:
        if game == "tic-tac-toe":
            await bot.say("The board positions are:\n```0|1|2\n-----\n3|4|5\n-----\n6|7|8```")
        #other games go here
    else:
        await bot.say("I'm sorry, I don't know that game")

@bot.command(pass_context=True)
async def emptyRoom(ctx, roomNo : int):
    """empties a specified gameroom. Plz don't abuse"""
    if roomNo < 1 or roomNo > NUM_GAMEROOMS:
        await bot.say("There is no gameroom with number: " + str(roomNo))
    else:
        channelName = "gameroom-" + str(roomNo)
        channel = discord.utils.get(ctx.message.server.channels, name=channelName)
        gameRooms = getSave.get("gamerooms.txt")
        gameRooms[int(channelName[9]) - 1] = []
        getSave.save(gameRooms, "gamerooms.txt")
        await bot.purge_from(channel)

@bot.command(pass_context=True)
async def newGame(ctx, *args):
    """starts a new game chosen by the challenger played with the challenged"""
    #args of form e.g. ("martian chess", "player 2", "player 3", "player 4"...)
    #need to check for correct number of players for each game

    if len(args) < 2:
        await bot.say("I'm sorry, I didn't understand that. The syntax is (where you are PLAYER1): $newGame GAMENAME PLAYER2 ...")
    else:
        chosenGame = args[0]
        challenged = args[1:]
        if chosenGame not in GAMES.keys():
            await bot.say("I'm sorry, I don't know: " + chosenGame)
        elif len(challenged) + 1 < GAMES[chosenGame][0] or len(challenged) > GAMES[chosenGame][1]:
            await bot.say("""Wrong number of players!
            The minimum number of players for this game are {}
            The maximum number of players for this game are {}
            """.format(GAMES[chosenGame][0], GAMES[chosenGame][1]))
        else:
            validPlayers = True
            mem = list(ctx.message.server.members)
            usernames = []
            for member in mem:
                usernames.append(member.name)
            for i in challenged:
                if i not in usernames:
                    await bot.say("Those are not valid players!")
                    validPlayers = False
                    break
            if validPlayers:
                gameRooms = getSave.get("gamerooms.txt")
                success = False 
                for i in range(len(gameRooms)):
                    if len(gameRooms[i]) < 1:
                        channelName = "gameroom-{}".format(i+1)
                        channel = discord.utils.get(ctx.message.server.channels, name=channelName)
                        await bot.say("You have been allocated gameroom-" + str(i+1))
                        
                        gameRooms[i].append(chosenGame)
                        gameRooms[i].append("1")
                        gameRooms[i].append(ctx.message.author.name)

                        game = GAMES[chosenGame][2]()

                        filename = "game" + str(i+1) + ".txt"
                        getSave.save(game, filename)
                        for player in challenged:
                            gameRooms[i].append(player)
                        getSave.save(gameRooms, "gamerooms.txt")
                        await bot.purge_from(channel)
                        welcome = "Welcome. This is a game of " + chosenGame + " between: " + ctx.message.author.name
                        for i in range(len(challenged)):
                            if i == len(challenged) - 1:
                               welcome += " and "
                            else:
                                welcome += ", "
                            welcome += challenged[i]
                        await bot.send_message(channel, welcome)
                        success = True
                        break
                if not success:
                    await bot.say("There are no gamerooms available, please try again later.")

@bot.command(pass_context=True)
async def place(ctx, move : int):
    """places a piece on the tic-tac-toe board"""
    channelName = ctx.message.channel.name

    syms = {0: 'X', 1: 'O'}

    try:
        room = int(channelName[-1])
    except ValueError:
        room = None 

    if not room: 
        await bot.say("You, sir, are not in a game room.")
    else:
        filename = "game{}.txt".format(room)
        gameRooms = getSave.get("gamerooms.txt")
        theBoard = getSave.get(filename)
        turn = int(gameRooms[room-1][1])
        if ctx.message.author.name == gameRooms[room-1][((turn + 1) % 2) + 2]:
            sym = syms[(turn + 1) % 2]
            try:
                theBoard.place(move, sym)
                iBoardFileName = "iBoard{}.png".format(room)
                theBoard.render().save(iBoardFileName)
                await bot.upload(iBoardFileName)
                winner = theBoard.getWinner()
                if not winner and turn < 9:
                    turn += 1
                    gameRooms[room-1][1] = str(turn)
                    getSave.save(theBoard, filename)
                    getSave.save(gameRooms, "gamerooms.txt")
                else:
                    if winner == "X":
                        await bot.say("X gon' give it to ya, since it won!\nVictory for: {} ".format(gameRooms[room-1][2]))
                    elif winner == "O":
                        await bot.say("OMG O won!!!\nVictory for: {}".format(gameRooms[room-1][3]))
                    else:
                        await bot.say("It's a tie.")
                    gameRooms[room-1] = []
                    getSave.save(gameRooms, "gamerooms.txt")
            except ticTacToe.IllegalMoveError as er:
                await bot.say("IllegalMoveError caught: {}".format(er.message))
        else:
            await bot.say("It ain't your turn sunshine.")

with open(TOKEN) as token:
    token = token.read()

bot.run(token)
