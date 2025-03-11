import discord
from discord.ext import commands

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game(f"type {self.bot.command_prefix}help"))
        print(f'Logged in as {self.bot.user}')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if "where my hug at" in message.content.lower():
            gif_url = "https://tenor.com/view/enage-kiss-anime-hug-kisara-gif-26118528"
            await message.channel.send(f"{message.author.mention}, here's your hug! 🤗 {gif_url}")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("What is blud waffling about?")
        else:
            # Handle other errors if needed
            await ctx.send(f"An error occurred: {str(error)}")