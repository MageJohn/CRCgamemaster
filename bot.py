import discord
from discord.ext import commands
import getSave
import ticTacToe
from PIL import Image
import os

# TO DO:
# add turn as an attribute of gamerooms.txt - Done!

TOKEN="token.txt"

description = '''CRC Gamemaster Bot'''
bot = commands.Bot(command_prefix='$', description=description)
knownGames = ("tic-tac-toe")

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
        await bot.say("There are no games currently in progress")

@bot.command()
async def helpttt():
    """Prints out board numbers"""
    await bot.say("```0|1|2\n-----\n3|4|5\n-----\n6|7|8```")

@bot.command()
async def emptyAll():
    """empties all game rooms. Plz don't abuse"""
    gamerooms = [[],[],[],[]]
    for i in range(4):
        lServers = list(bot.servers)
        server = lServers[0]
        channelName = "gameroom-" + str(i+1)
        channel = discord.utils.get(bot.get_all_channels(), server__name='CRC Buddies', name=channelName)
        await bot.purge_from(channel)
    getSave.save(gamerooms, "gamerooms.txt")

@bot.command(pass_context=True)
async def newGame(ctx, *args):
    """starts a new game chosen by the challenger played with the challenged"""
    #args of form e.g. ("martian chess", "player 2", "player 3", "player 4"...)
    #need to check for correct number of players for each game
    chosenGame = args[0]
    if len(args) >= 2:
        if chosenGame in knownGames:
            gameRooms = getSave.get("gamerooms.txt")
            mem = ctx.message.server.members
            names = []
            for member in mem:
                names.append(member.name)
            validPlayers = True
            challenged = []
            for i in range(len(args)-1):
                if args[i+1] not in names:
                    validPlayers = False
                    break
                else:
                    challenged.append(args[i+1])

            if validPlayers:
                success = False 
                for i in range(len(gameRooms)):
                    if len(gameRooms[i]) < 1:
                        channelName = "gameroom-" + str(i+1)
                        channel = discord.utils.get(bot.get_all_channels(), server__name='CRC Buddies', name=channelName)
                        await bot.say("You have been allocated gameroom-" + str(i+1))

                        gameRooms[i].append(chosenGame)
                        gameRooms[i].append("1")
                        gameRooms[i].append(ctx.message.author.name)
                        game = None
                        if chosenGame == "tic-tac-toe":
                            game = ticTacToe.TicTacToe()
                        #other games go here
                        filename = "game" + str(i+1) + ".txt"
                        getSave.save(game, filename)
                        for player in challenged:
                            gameRooms[i].append(player)
                        getSave.save(gameRooms, "gamerooms.txt")
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
            else:
                await bot.say("Those are not valid players!")
        else:
            await bot.say("I'm sorry, I don't know: \"" + args[0] + "\"")
    else:
        await bot.say("I'm sorry, I didn't understand that.")

@bot.command(pass_context=True)
async def place(ctx, move : int):
    """places a piece on the tic-tac-toe board"""
    channel = ctx.message.channel.name
    room = 0
    if channel == "gameroom-1":
        room = 1
    elif channel == "gameroom-2":
        room = 2
    elif channel == "gameroom-3":
        room = 3
    elif channel == "gameroom-4":
        room = 4

    filename = "game" + str(room) + ".txt"
    gameRooms = getSave.get("gamerooms.txt")
    theBoard = getSave.get(filename)
    if room > 0:
        turn = int(gameRooms[room-1][1])
        if ctx.message.author.name == gameRooms[room-1][((turn + 1) % 2) + 2]:
            sym = ""
            if turn % 2 == 1:
                sym = "X"
            else:
                sym = "O"
            try:
                theBoard.place(move, sym)
                iBoard = theBoard.render()
                iBoardFileName = "iBoard" + str(room) + ".png"
                iBoard.save(iBoardFileName)
                await bot.upload(iBoardFileName)
                if theBoard.getWinner() == None:
                    turn += 1
                    gameRooms[room-1][1] = str(turn)
                    getSave.save(theBoard, filename)
                    getSave.save(gameRooms, "gamerooms.txt")
                else:
                    if theBoard.getWinner() == "X":
                        await bot.say("X gon' give it to ya, since it won!\nVictory for: " + gameRooms[room-1][2])
                    elif theBoard.getWinner() == "O":
                        await bot.say("OMG O won!!!\nVictory for: " + gameRoom[room-1][3])
                    else:
                        await bot.say("It's a tie.")
                    gameRooms[room-1] = []
                    getSave.save(gameRooms, "gamerooms.txt")
            except ticTacToe.IllegalMoveError as er:
                await bot.say("IllegalMoveError caught: {}".format(er.message))
        else:
            await bot.say("It ain't your turn sunshine.")
    else:
        await bot.say("You, sir, are not in a gameroom.")

with open(TOKEN) as token:
    token = token.read()

bot.run(token)
