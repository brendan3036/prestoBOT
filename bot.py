import discord
import asyncio
from discord.utils import get

intents = discord.Intents.default()
intents.members = True

TOKEN = 'Nzg2Nzk2NzQ1NjA1NjQ0Mjk4.X9Lnkg.VlQDkrVDI69B8CLBlzSeq_giJC4'

client = discord.Client(intents = intents)
check = "\N{WHITE HEAVY CHECK MARK}"
pug_active = False

@client.event
async def on_message(message):
    global pug_active
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
            # Keep track of all users who react with the check until we reach 9 (8 players + 1 bot).
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

# Returns whether we have enough reactions on the desired message or not. 
def check_count_reaction(emoji, desired_count, message):
    def predicate(reaction, user):
        return reaction.message == message and reaction.emoji == emoji and reaction.count>= desired_count
    return predicate


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

client.run(TOKEN)