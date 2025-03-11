import discord
from discord.ext import commands, menus
import aiosqlite

class LeaderboardMenu(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=10)  # Show 10 users per page

    async def format_page(self, menu, entries):
        page_num = menu.current_page + 1
        total_pages = self.get_max_pages()
        embed = discord.Embed(title="📜 Server Leaderboard", color=discord.Color.gold())

        for idx, (user_id, username, balance) in enumerate(entries, start=(menu.current_page * self.per_page) + 1):
            embed.add_field(name=f"#{idx} {username}", value=f"💰 {balance} doubloons", inline=False)

        embed.set_footer(text=f"Page {page_num}/{total_pages}")
        return embed

class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None

    async def on_ready(self):
        await self.connect_db()
    
    async def connect_db(self):
        self.db = await aiosqlite.connect("economy.db")
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER,
                guild_id INTEGER,
                username TEXT NOT NULL,
                balance INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, guild_id)
            )
        """)
        await self.db.commit()

    async def ensure_user_exists(self, user_id, guild_id, username):
        """Ensures user exists for the specific guild."""
        await self.db.execute(
            "INSERT OR IGNORE INTO users (user_id, guild_id, username, balance) VALUES (?, ?, ?, 0)", 
            (user_id, guild_id, username)
        )
        await self.db.commit()

    async def get_balance(self, user_id, guild_id, username):
        await self.ensure_user_exists(user_id, guild_id, username)
        async with self.db.execute("SELECT balance FROM users WHERE user_id = ? AND guild_id = ?", (user_id, guild_id)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def update_balance(self, user_id, guild_id, username, amount):
        await self.ensure_user_exists(user_id, guild_id, username)
        await self.db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ? AND guild_id = ?", 
            (amount, user_id, guild_id)
        )
        await self.db.commit()
        print(f"Updated balance for {username} to {amount} in guild {guild_id}.")  # Debugging line


    @commands.command(name="balance", aliases=["bal"], help="Check your current balance of doubloons")
    async def balance(self, ctx):
        balance = await self.get_balance(ctx.author.id, ctx.guild.id, ctx.author.name)
        await ctx.send(f"{ctx.author.mention}, you currently have **💰 {balance} doubloons**.")

    @commands.command(name="transfer", aliases=["give"], help="Transfer doubloons to another user")
    async def transfer(self, ctx, recipient: discord.Member, amount: int):
        if recipient == ctx.author:
            await ctx.send(f"{ctx.author.mention}, you can't transfer doubloons to yourself!")
            return

        if amount <= 0:
            await ctx.send(f"{ctx.author.mention}, you must send a **positive** amount of doubloons!")
            return

        sender_balance = await self.get_balance(ctx.author.id, ctx.guild.id, ctx.author.name)
        if sender_balance < amount:
            await ctx.send(f"{ctx.author.mention}, you don't have enough doubloons to transfer!")
            return

        await self.update_balance(ctx.author.id, ctx.guild.id, ctx.author.name, -amount)
        await self.update_balance(recipient.id, ctx.guild.id, recipient.name, amount)
        await ctx.send(f"💸 {ctx.author.mention} has transferred **{amount} doubloons** to {recipient.mention}!")

    @commands.command(name="leaderboard", aliases=["all_balances", "balances"], help="Display top users in this server")
    async def all_balances(self, ctx):
        guild_id = ctx.guild.id
        async with self.db.execute(
            "SELECT user_id, username, balance FROM users WHERE guild_id = ? ORDER BY balance DESC", 
            (guild_id,)
        ) as cursor:
            results = await cursor.fetchall()

        if not results:
            await ctx.send("No economy data for this server yet!")
            return

        menu = menus.MenuPages(source=LeaderboardMenu(results), clear_reactions_after=True)
        await menu.start(ctx)

    @commands.command(name="reset_db", help="Deletes all user data from the economy database")
    @commands.has_permissions(administrator=True)
    async def reset_db(self, ctx):
        guild_id = ctx.guild.id  # Restrict to current server only
        await self.db.execute("DELETE FROM users WHERE guild_id = ?", (guild_id,))
        await self.db.commit()
        await ctx.send(f"🗑 The economy database for **{ctx.guild.name}** has been reset!")

    @commands.command(name="add_money", help="add money to account")
    @commands.has_permissions(administrator=True)
    async def add_money(self, ctx, member: discord.Member, amount: int):
        """Allows an admin to add money to a user's account."""
        
        if amount <= 0:
            await ctx.send("Amount must be greater than 0.")
            return

        # Update the balance in the database
        await self.update_balance(member.id, ctx.guild.id, member.name, amount)

        # Fetch the updated balance
        new_balance = await self.get_balance(member.id, ctx.guild.id, member.name)

        if new_balance is not None:
            await ctx.send(f"Added {amount} doubloons to {member.mention}. Their new balance is {new_balance} doubloons.")
        else:
            await ctx.send("Something went wrong while updating the balance.")

    async def cog_load(self):
        await self.connect_db()

    async def cog_unload(self):
        if self.db:
            await self.db.close()
