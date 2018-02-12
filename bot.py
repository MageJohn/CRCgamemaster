import discord
from discord.ext import commands
import utils
import ticTacToe
import sevens
import textwrap
from gtts import gTTS
import opuslib

TOKEN="token.txt"

description = '''CRC Gamemaster Bot'''
bot = commands.Bot(command_prefix='$', description=description)
# format: {gameName: (minPlayers, maxPlayers, gameObject), ..}
GAMES = {"tic-tac-toe": (2, 2, ticTacToe.TicTacToe), "sevens": (3, 7, sevens.Sevens)}

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(pass_context=True)
async def sayThis(ctx, content : str):
    """Speaks a provided string in the \'general\' voice channel.Enclose in \"\". Abusers will be banned."""

    #if not discord.opus.is_loaded():
        #discord.opus.load_opus()
    message = ctx.message
    channel = message.channel
    print (channel.name)
    server = channel.server
    print (server.name)
    channels = server.channels
    for chan in channels:
        print(chan.name)
    generalVoiceChannel = None
    for chan in channels:
        if chan.type == 'voice':
            print("{} is a voice channel".format(chan.name))
    print("\n\n***********************************\n\n")
    generalVoiceChannel = discord.utils.find(lambda c: c.type == 'voice', channels)
    #generalVoiceChannel = discord.utils.get(ctx.message.server.channels, name='General', type='voice')
    print(generalVoiceChannel.name)
    if generalVoiceChannel is not None:
        print(generalVoiceChannel.name)
    else:
        print("None.")
    await bot.join_voice_channel(generalVoiceChannel)
    spoken = utils.get("spoken.txt")
    authorName = ctx.message.author.name
    textToSay = ("{} says {}".format(authorName, content))
    if spoken[authorName]:
        spoken[authorName].append(content)
    else:
        spoken[authorName] = [content]

    tts = gTTS(text=textToSay, lang='en')
    tts.save("speech{}{}.mp3".format(authorName.replace(" ", "-"), len(spoken[authorName])))

@bot.command(pass_context=True)
async def resetAll(ctx):
    """Resets all the rooms on the current server. Mods only"""
    if not discord.utils.find(lambda r: r.name == 'Mods', ctx.message.author.roles):
        return await bot.say("You need to be a mod to do that.")

    gameRooms = {}
    gameRooms[ctx.message.server.name] = [utils.Room(c) for c in ctx.message.server.channels if c.name.startswith('gameroom-')]

    utils.save(gameRooms, "gamerooms.txt")

@bot.command()
async def rooms():
    """Lists players in each gameroom and the game they're playing"""
    gameRooms = utils.get("gamerooms.txt")
    response = ["The games in progress are:"]
    for room in gameRooms[ctx.message.server.name]:
        if room.game:
            response.append("{0}: {}{} playing {}".format(room.channel.name,
                                                          ", ".join(room.players[:-1]),
                                                          ", and {} ".format(room.players[-1]),
                                                          room.game))
    if len(response) > 1:
        await bot.say("\n".join(response))
    else:
        await bot.say("There are no games currently in progress.")

@bot.command()
async def guide(game : str):
    """Outputs guide to game"""
    if game in GAMES:
        if game == "tic-tac-toe":
            await bot.say("The board positions are:")
            await bot.say(textwrap.dedent("""```\
                                             0|1|2
                                             -----
                                             3|4|5
                                             -----
                                             6|7|8```"""))
            await bot.say("The command to place your piece at position 0 is $place 0")
        #other games go here
    else:
        await bot.say("I'm sorry, I don't know that game")

@bot.command(pass_context=True)
async def newGame(ctx, *args):
    """starts a new game chosen by the challenger played with the challenged"""
    # args of form e.g. ("martian chess", "player 2", "player 3", "player 4"...)
    # need to check for correct number of players for each game

    if len(args) < 2:
        return await bot.say("I'm sorry, I didn't understand that. The syntax is: $newGame GAMENAME PlAYER [PLAYERS...]")
    chosenGame = args[0]
    challenged = args[1:]
    gameRooms = utils.get("gamerooms.txt")
    if chosenGame not in GAMES.keys():
        return await bot.say("I'm sorry, I don't know how to play \"{}\".".format(choenGame))
    elif GAMES[chosenGame][0] == GAMES[chosenGame][1] and\
            len(challenged) + 1 != GAMES[chosenGame][0]:
        return await bot.say("Wrong number of players! This game requires {} players.".format(GAMES[chosenGame][0]))
    elif len(challenged) + 1 < GAMES[chosenGame][0] or\
            len(challenged) + 1 > GAMES[chosenGame][1]:
        return await bot.say("Wrong number of players! This game has between {} and {} players.".format(GAMES[chosenGame][0], GAMES[chosenGame][1]))

    names = [mem.name for mem in ctx.message.server.members]
    for i in challenged:
        if i not in names:
            return await bot.say("Those are not valid players! {}.".format(", ".join(challenged)))
    
    for room in gameRooms[ctx.message.server.name]:
        if not room.game:
            break
        room = None

    if not room:
        return await bot.say("There are no games available, please try again later.")

    await bot.say("You have been allocated {}".format(room.channel.name))

    room.game = chosenGame
    room.turn = 0
    room.players = [ctx.message.author.name]
    room.game_state = GAMES[chosenGame][2]()
    room.players += challenged
    utils.save(gameRooms, "gamerooms.txt")
    await bot.purge_from(room.channel)
    welcome = "Welcome. This is a game of {} between: {}".format(chosenGame, ctx.message.author.name)
    for i, name in enumerate(challenged):
        if i == len(challenged) - 1:
            welcome += ", and "
        else:
            welcome += ", "
        welcome += challenged[i]

    await bot.send_message(room.channel, welcome)

@bot.command(pass_context=True)
async def place(ctx, move):
    """places a piece on the tic-tac-toe board"""
    syms = {0: 'X', 1: 'O'}

    if not ctx.message.channel.name.startswith('gameroom-'):
        return await bot.say("You, sir, are not in a gameroom.")

    gameRooms = utils.get("gamerooms.txt")
    for room in gameRooms[ctx.message.server.name]:
        if room.channel == ctx.message.channel:
            break

    if not room.game:
        return await bot.say("There's no game here!")

    if ctx.message.author.name != room.players[room.turn % 2]:
        return await bot.say("It ain't your turn sunshine.")

    sym = syms[room.turn % 2]

    try:
        room.game_state.place(int(move), sym)
    except utils.IllegalMoveError as er:
        return await bot.say("You can't do that! {}".format(er.message))
    except ValueError:
        return await bot.say("Your move must be a number! You put: {}".format(move))

    boardRenderFile = "board_{}_{}.png".format(ctx.message.server, ctx.message.channel)
    room.game_state.render().save(boardRenderFile)
    await bot.upload(boardRenderFile)

    winner = room.game_state.getWinner()
    if not winner and room.turn < 8:
        room.turn += 1
        utils.save(gameRooms, "gamerooms.txt")
    else:
        if winner:
            await bot.say("The winner is to be programmed.")
        else:
            await bot.say("It's a tie.")
        gamRooms[ctx.message.server] = room.__init__(room.channel)
        utils.save(gameRooms, "gameRooms.txt")

if __name__ == "__main__":
    with open(TOKEN) as token:
        token = token.read()

    bot.run(token)
