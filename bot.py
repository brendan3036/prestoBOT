import discord
import asyncio
import random
from discord.utils import get

intents = discord.Intents.default()
intents.members = True

# TOKEN = 'TOKEN HERE'

client = discord.Client(intents = intents)
check = "\N{WHITE HEAVY CHECK MARK}"
pug_active = False
rock_paper_scissors_game = False
player_wins = 0
bot_wins = 0
moves = ['🪨', '📜', '✂️']

@client.event
async def on_message(message):
    global pug_active
    global rock_paper_scissors_game
    author = message.author
    # We do not want the bot to reply to itself
    if author == client.user:
        return
    if message.content == "!pug":
        # For a small group/discord, we don't need more than one pug queue active at once.
        if pug_active == True:
            await message.delete()
            return
        else:
            pug_active = True
            # Set channel to the pug channel
            channel = get(message.author.guild.channels, name = "pug")
            # Our pug message, and adding the initial check reaction to it.
            msg = await channel.send('React to play! You will be pinged once enough have reacted.')
            await msg.add_reaction(check)
            # Keep track of all users who react with the check until we reach X + 1 Reactions (X players + 1 Bot reaction)
            reaction, user = await client.wait_for('reaction_add', check=check_count_reaction(check, 3, msg))
            users = await reaction.users().flatten()
            # Remove the bot from user list.
            users.remove(client.user)
            # Mention everyone who wanted to play so they see it's time.
            await channel.send(f"{', '.join(m.mention for m in users)} are playing! Get in voice.")
            # Clear the channel after 5 minutes
            pug_active = False
            await asyncio.sleep(300)
            await channel.purge()
    elif message.content == "!rockpaperscissors" or message.content == "!rpc":
        if rock_paper_scissors_game == True:
            await message.delete()
            return
        else:
            rock_paper_scissors_game = True
            # We will do rock paper scissors in #general
            channel = get(message.author.guild.channels, name = "rockpaperscissors")
            msg = await channel.send('Rock, paper, scissors! (First to 3)\nReact with your weapon of choice.')
            await msg.add_reaction("🪨")
            await msg.add_reaction("📜")
            await msg.add_reaction("✂️")
            await message.delete()

# Returns whether we have enough reactions on the desired message or not. 
def check_count_reaction(emoji, desired_count, message):
    def predicate(reaction, user):
        return reaction.message == message and reaction.emoji == emoji and reaction.count>= desired_count
    return predicate

@client.event
async def on_reaction_add(reaction, user):
    global player_wins, bot_wins, rock_paper_scissors_game, moves
    channel = get(reaction.message.author.guild.channels, name = "rockpaperscissors")
    # If the reaction is on the bot's post that starts with 'Rock' and we are indeed playing a game of rock paper scissors:
    if rock_paper_scissors_game == True and reaction.message.content.startswith("Rock") and user.id != reaction.message.author.id:
        await reaction.remove(user)
        await assessRound(channel, reaction.emoji, random.choice(moves))

async def assessRound(channel, player_choice, bot_choice):
    global player_wins, bot_wins, rock_paper_scissors_game
    if player_choice == bot_choice:
        await channel.send("Your "+player_choice + " and My "+bot_choice + " do nothing : Try again.")
    # All of the player winning scenarios.
    elif (player_choice == "✂️" and bot_choice == "📜") or (player_choice == "🪨" and bot_choice == "✂️") or (player_choice == "📜" and bot_choice == "🪨"):
        player_wins += 1
        await channel.send("Your "+player_choice + " beats My "+bot_choice + " : You win a point! Score: "+str(player_wins) + " - " + str(bot_wins))
        if player_wins == 3:
            await channel.send("Okay, I've had enough. GG")
            await resetGame(channel)  
    # All of the bot winning scenarios.
    elif (player_choice == "📜" and bot_choice == "✂️") or (player_choice == "✂️" and bot_choice == "🪨") or (player_choice == "🪨" and bot_choice == "📜"):
        bot_wins += 1
        await channel.send("Your "+player_choice + " loses to My "+bot_choice + " : I win a point! Score: "+str(player_wins) + " - " + str(bot_wins))
        if bot_wins == 3:
            await channel.send("Easyyy win for me.")
            await resetGame(channel)

async def resetGame(channel):
    global rock_paper_scissors_game, player_wins, bot_wins
    player_wins = 0
    bot_wins = 0
    rock_paper_scissors_game = False
    await asyncio.sleep(3)
    await channel.purge()

@client.event
async def on_member_join(member): 
    # Fetch the starter role
    role = get(member.guild.roles, id = 787106145399078953)
    # Give it to the user
    await member.add_roles(role)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    # Clear pug channel since we just re-started.
    channel = client.get_channel(786874251667439636)
    await channel.purge()

client.run(TOKEN)