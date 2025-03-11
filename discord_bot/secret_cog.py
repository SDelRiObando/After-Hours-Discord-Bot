import discord
from discord.ext import commands

class secret_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_user_id(self, guild: discord.Guild, username: str) -> int | None:
        for member in guild.members:
            if member.name == username or member.display_name == username:
                return member.id
        return None

    @commands.command(name="brian", help="Ask Brian if he's sent that email and post an image")
    async def brian(self, ctx):
        image_path = "reactions\\WhatDoesBrianEvenDo.jpg"
        gif_url = "https://tenor.com/view/kneel-overlord-anime-bow-pay-respect-gif-17682779"
        # Dynamically get Brian's UID using the helper function by username
        brian_id = await self.get_user_id(ctx.guild, "brianc8")  # Use the username here
        
        if brian_id and brian_id == ctx.author.id:
            member = ctx.guild.get_member(brian_id)
            if member:
                try:
                    await ctx.send(f"{member.mention} How may I serve you my glorious king? {gif_url}")
                except FileNotFoundError:
                    await ctx.send("Oops, I couldn't find the image. Please check the file path.")
            else:
                await ctx.send("Couldn't find Brianc. Please check the username.")
        elif brian_id:
            member = ctx.guild.get_member(brian_id)
            if member:
                try:
                    await ctx.send(f"{member.mention}, have you sent that email yet?", file=discord.File(image_path))
                except FileNotFoundError:
                    await ctx.send("Oops, I couldn't find the image. Please check the file path.")
        else:
            await ctx.send("Couldn't find Brianc. Please check the username.")

    @commands.command(name="josh", help="Let's go to Jollibee and send a video")
    async def josh(self, ctx):
        video_path = "reactions\\joshisfilipino.mp4"  # Ensure the path is correct for your environment
        try:
            await ctx.send("Let's go to Jollibee!", file=discord.File(video_path))
        except FileNotFoundError:
            await ctx.send("Oops, I couldn't find the video. Please check the file path.")

    @commands.command(name="paul", help="Give Paul the business")
    async def paul(self, ctx):
        image_path = "reactions\\GonKick.jpg"
        
        # Dynamically get Paul's UID using the helper function by username
        paul_id = await self.get_user_id(ctx.guild, "rosaria.tara")  # Use the username here
        
        if paul_id:
            member = ctx.guild.get_member(paul_id)
            if member:
                try:
                    await ctx.send(f"{member.mention} Alright bud, thats enough out of you.", file=discord.File(image_path))
                except FileNotFoundError:
                    await ctx.send("Oops, I couldn't find the image. Please check the file path.")
        else:
            await ctx.send("Couldn't find Paul. Please check the username.")

    @commands.command(name="ozzy", help="Give Ozzy some love")
    async def ozzy(self, ctx):
        gif_url = "https://tenor.com/view/syno-i-love-you-syno-synowithazero-gif-2023483407273504018"
        
        # Dynamically get Ozzy's UID using the helper function by username
        ozzy_id = await self.get_user_id(ctx.guild, "ozzytadashi")  # Use the username here
        
        if ozzy_id:
            member = ctx.guild.get_member(ozzy_id)
            if member:
                try:
                    await ctx.send(f"{member.mention}Ozzy-chan! daisuki da yo!{gif_url}")
                except FileNotFoundError:
                    await ctx.send("Oops, I couldn't find the image. Please check the file path.")
        else:
            await ctx.send("Couldn't find Ozzy. Please check the username.")

    @commands.command(name="norma", help="The Norma Command")
    async def norma(self, ctx):
        norma_gif_url = "https://tenor.com/view/berrycrepe-wake-up-peg-gif-21235142"
        other_gif_url = "https://tenor.com/view/chiaki-nanami-chiaki-sleep-chiaki-chiaki-a-mimir-danganronpa-gif-24378497"

        # Dynamically get Ozzy's UID using the helper function by username
        norma_id = await self.get_user_id(ctx.guild, "norms_s")  # Use the username here

        if norma_id and norma_id == ctx.author.id:
            mikey_id = await self.get_user_id(ctx.guild, "cheezuscrust")  # Use the username here
            if mikey_id:
                member = ctx.guild.get_member(mikey_id)
                if member:
                    try:
                        await ctx.send(f"{member.mention} {norma_gif_url}")
                    except FileNotFoundError:
                        await ctx.send("Oops, I couldn't find the image. Please check the file path.")
                else:
                    await ctx.send("Couldn't find Mikey. Please check the username.")
        elif norma_id:
            member = ctx.guild.get_member(norma_id)
            if member:
                try:
                    await ctx.send(f"{member.mention} It's 4pm Wake UP!!! {other_gif_url}")
                except FileNotFoundError:
                    await ctx.send("Oops, I couldn't find the image. Please check the file path.")
        else:
            await ctx.send("Couldn't find Norma. Please check the username.")

    @commands.command(name="riggy", help="Give Riggy the business")
    async def riggy(self, ctx):
        gif_url = "https://tenor.com/view/mask-iron-man-drake-rapper-gif-15913037"
        
        # Dynamically get Riggy's UID using the helper function by username
        riggy_id = await self.get_user_id(ctx.guild, "riggy004")  # Use the username here
        
        if riggy_id:
            member = ctx.guild.get_member(riggy_id)
            if member:
                try:
                    await ctx.send(f"{member.mention} Stop rigging. {gif_url}")
                except FileNotFoundError:
                    await ctx.send("Oops, I couldn't find the image. Please check the file path.")
        else:
            await ctx.send("Couldn't find Riggy. Please check the username.")

    @commands.command(name="strongest", help="Send a kiss gif to the mentioned user")
    async def strongest(self, ctx):
        gif_url = "reactions\\Strongest.gif"
        brian_id = await self.get_user_id(ctx.guild, "brianc8")  # Use the username here
        
        if brian_id:
            member = ctx.guild.get_member(brian_id)
            if member:
                try:
                    await ctx.send(f"You mean {member.mention}?", file=discord.File(gif_url))
                except FileNotFoundError:
                    await ctx.send("Oops, I couldn't find the image. Please check the file path.")
        else:
            await ctx.send("Couldn't find Brianc. Please check the username.")

    @commands.command(name='get-uid', help="Get the Discord user ID by mention or username")
    async def get_uid(self, ctx, user: discord.User = None):
        if user is not None:
            await ctx.send(f"{user.name}'s User ID: `{user.id}`")
        else:
            await ctx.send("Please mention a valid user or provide their username.")