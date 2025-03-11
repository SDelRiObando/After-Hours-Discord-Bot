import discord
from discord.ext import commands
import os, asyncio


#import all of the cogs
from help_cog import help_cog
from music_cog import music_cog
from secret_cog import secret_cog
from games_cog import GamesCog
from games_cog import slot_machine_cog
from economy_cog import EconomyCog
from event_cog import EventsCog
from horoscope_cog import HoroscopeCog
from chess_cog import ChessCog

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!!', intents=intents)

#remove the default help command so that we can write out own
bot.remove_command('help')

@bot.command()
async def bruh(ctx, arg):
    await ctx.send(arg)

@bot.command()
async def capping(ctx, flag: bool):
    if flag:
        await ctx.send("TRUEEE!")
    else:
        await ctx.send("LIES!")

@bot.command()
async def add(ctx, *args):
    numbers = [int(arg) for arg in args]
    result = sum(numbers)
    await ctx.send(f'{result}')

@bot.command(rest_is_raw=False)
async def hype_me_up(ctx, *, phrase):    
    await ctx.send(f"""🌟 Woah! Did you really "{phrase}"! 🌟
That sounds absolutely AMAZING!! 😱💥🔥 Keep it up! 🎉""")

def to_upper(argument):
    return argument.upper()

@bot.command()
async def up(ctx, *, content: to_upper):
    await ctx.send(content)


class CensorConverter(commands.Converter):
    def __init__(self, banned_words=None, replacement="***"):
        # Store the list of words to censor (default: empty list)
        self.banned_words = banned_words or []
        self.replacement = replacement  # What to replace banned words with

    async def convert(self, ctx, argument):
        words = argument.split()  # Split input into words
        censored_message = [
            self.replacement if word.lower() in self.banned_words else word for word in words
        ]
        return " ".join(censored_message)  # Return the modified message
    
@bot.command()
async def say(ctx, *, message: CensorConverter(banned_words=["spoiler", "badword"], replacement="🤐")):
    await ctx.send(message)

@bot.hybrid_group(fallback="get")
async def tag(ctx, name):
    await ctx.send(f"Showing tag: {name}")

@tag.command()
async def create(ctx, name):
    await ctx.send(f"Created tag: {name}")

@bot.hybrid_command()
async def test(ctx):
    await ctx.send("This is a hybrid command!")

with open('C:\\Users\\Santiago\\Documents\\GitHub\\After-Hours-Discord-Bot\\discord_bot\\token.txt', 'r') as file:
    token=file.readlines()[0]

async def main():
    print("Starting bot...")
    async with bot:
        await bot.add_cog(help_cog(bot))
        await bot.add_cog(EventsCog(bot))
        await bot.add_cog(HoroscopeCog(bot))
        await bot.add_cog(EconomyCog(bot))
        await bot.add_cog(music_cog(bot))
        await bot.add_cog(secret_cog(bot))
        await bot.add_cog(GamesCog(bot))
        await bot.add_cog(slot_machine_cog(bot))
        await bot.add_cog(ChessCog(bot))
        await bot.start(token)

asyncio.run(main())