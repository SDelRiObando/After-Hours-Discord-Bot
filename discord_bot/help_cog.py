import discord
from discord.ext import commands

class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.text_channel_list = []
        self.pages = []
        self.current_page = 0
        self.set_pages()

    def set_pages(self):
        """Creates multiple pages for the help command using embeds."""
        
        # Page 1: General Commands
        general_commands = f"""
        **1.) help**: Displays all available commands\n
        **2.) hello**: Say hi to Chiaki\n
        **3.) morning**: Send a good morning message\n  
        **4.) prefix**: Change the command prefix \n
        **5.) kiss @user**: Send a virtual kiss to @user
        """
        general_embed = discord.Embed(title="📜 General Commands\nUsePrefix: '!!'", description=general_commands, color=discord.Color.purple())

        # Page 2: Music Commands
        music_commands = f"""
        **1.) q**: Displays the current music queue\n
        **2.) p <keywords>**: Play a song from YouTube\n
        **3.) skip**: Skip the current song\n
        **4.) clear**: Stop music & clear the queue\n 
        **5.) stop**: Disconnect the bot from voice chat\n
        **6.) pause**: Pause/resume the song\n
        **8.) resume**: Resume playing the current song\n
        **9.) remove**: Remove the last song from the queue
        """
        music_embed = discord.Embed(title="🎵 Music Commands\nUsePrefix: '!!'", description=music_commands, color=discord.Color.blue())

        # Page 3: Games
        games_commands = f"""
        **1.) c4 @opponent**: Start a Connect Four game\n
        **2.) russian**: Play Russian Roulette  
        """
        games_embed = discord.Embed(title="🎮 Game Commands\nUsePrefix: '!!'", description=games_commands, color=discord.Color.green())

        # Store pages in list
        self.pages = [general_embed, music_embed, games_embed]

    @commands.command(name="help", help="Displays all the available commands")
    async def help(self, ctx):
        """Sends the first help page and adds reactions for navigation."""
        current_page = 0
        message = await ctx.send(embed=self.pages[current_page])
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in ["⬅️", "➡️"]

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)

                if str(reaction.emoji) == "➡️":
                    if current_page < len(self.pages) - 1:
                        current_page += 1
                        await message.edit(embed=self.pages[current_page])
                elif str(reaction.emoji) == "⬅️":
                    if current_page > 0:
                        current_page -= 1
                        await message.edit(embed=self.pages[current_page])

                await message.remove_reaction(reaction, user)

            except TimeoutError:
                break  # If no reaction after 60 seconds, stop the loop

    @commands.command(name="prefix", help="Change bot prefix")
    async def prefix(self, ctx, *args):
        self.bot.command_prefix = " ".join(args)
        self.set_message()
        await ctx.send(f"prefix set to **'{self.bot.command_prefix}'**")
        await self.bot.change_presence(activity=discord.Game(f"type {self.bot.command_prefix}help"))

    @commands.command(name="send_to_all", help="send a message to all members")
    async def send_to_all(self, msg):
        for text_channel in self.text_channel_list:
            await text_channel.send(msg)

    # Add the hello command
    @commands.command(name="hello", aliases=["hi", "hey", "yo","oi"], help="Responds with a friendly greeting")
    async def hello(self, ctx):
        await ctx.send("What's cooking, good looking?")
    
    @commands.command(name="kiss", aliases=["kis","smooch"], help="Send a kiss gif to the mentioned user")
    async def kiss(self, ctx, member: discord.Member):
        gif_url = "https://tenor.com/view/hop-on-fortnite-fortnite-anime-kiss-meme-gif-27334812"
        await ctx.send(f"{ctx.author.mention} sent a kiss to {member.mention}! {gif_url}")

    @commands.command(name="glaze", help="SGlaze the mentioned user")
    async def glaze(self, ctx, member: discord.Member):
        gif_url = "https://tenor.com/view/donut-glaze-satisfying-gif-13180530"
        await ctx.send(f"{ctx.author.mention} thinks {member.mention} is the goat! {gif_url}")

    @commands.command(name="morning", aliases=["Morning"], help="Greet everyone and post an image")
    async def morning(self, ctx):
        image_path = "reactions\\Bran_Ohayo.png"  # Ensure the path is correct for your environment
        try:
            await ctx.send("Ohayo gozaimasu minasan~", file=discord.File(image_path))
        except FileNotFoundError:
            await ctx.send("Oops, I couldn't find the image. Please check the file path.")

    @commands.command(name="night",aliases=["Night"], help="Tell Everyone Good Night and post an image")
    async def night(self, ctx):
        image_path = "reactions\\Brian_mimir.png"  # Ensure the path is correct for your environment
        try:
            await ctx.send("A mimir", file=discord.File(image_path))
        except FileNotFoundError:
            await ctx.send("Oops, I couldn't find the image. Please check the file path.")
    
    @commands.command(name="kill", aliases=["kil","murder"], help="assassinate a member")
    async def kill(self, ctx, member: discord.Member):
        image_path = "reactions\\Chiaki_Shoot.png"
        try:
            await ctx.send(f"Nothing personal {member.mention}!", file=discord.File(image_path))
        except FileNotFoundError:
            await ctx.send("Oops, I couldn't find the image. Please check the file path.")
