import discord
from discord.ext import commands
import random
import asyncio

class GamesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.columns = 7
        self.rows = 6
        self.empty_slot = "⚪"
        self.player_pieces = ["🔴", "🟡"]  # Red for Player 1, Yellow for Player 2
        self.number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]
    
    async def get_user_id(self, guild: discord.Guild, username: str) -> int | None:
        for member in guild.members:
            if member.name == username or member.display_name == username:
                return member.id
        return None
    
    async def get_balance(self, user_id, guild_id, username):
        """Fetch balance from economy_cog."""
        economy_cog = self.bot.get_cog("EconomyCog")
        if economy_cog:
            return await economy_cog.get_balance(user_id, guild_id, username)
        return None  # Return None if EconomyCog isn't found

    async def update_balance(self, user_id, guild_id, username, amount):
        """Update balance in economy_cog."""
        economy_cog = self.bot.get_cog("EconomyCog")
        if economy_cog:
            await economy_cog.update_balance(user_id, guild_id, username, amount)


    @commands.command(name="russian-roulette", aliases=["rr"], help="Play Russian Roulette with the bot!")
    async def russian_roulette(self, ctx):
        """Play a game of Russian Roulette with the bot."""
        
        # Attempt to send the image prompt
        image_path = "reactions/Russian_Roulette_Choose.png"
        try:
            await ctx.send(file=discord.File(image_path))
        except FileNotFoundError:
            await ctx.send("Oops, I couldn't find the image. Please check the file path.")

        await ctx.send("Alright chief, how many bullets? (1-5)")

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel and message.content.isdigit()

        try:
            response = await self.bot.wait_for('message', check=check, timeout=30.0)
            bullets_in_chamber = int(response.content)

            # Handling invalid bullet count
            if bullets_in_chamber < 1 or bullets_in_chamber > 5:
                if bullets_in_chamber >= 6:
                    # Get Paul's user ID dynamically
                    paul_id = await self.get_user_id(ctx.guild, "rosaria.tara")
                    
                    if paul_id and int(paul_id) == ctx.author.id:
                        shut_up_paul = "reactions/Chiaki_Silence.jpg"
                        member = ctx.guild.get_member(paul_id)
                        if member:
                            try:
                                await ctx.send(f"I've had enough of you {member.mention}", file=discord.File(shut_up_paul))
                                await ctx.send("*BANG!* Sayonara chief.")
                                return
                            except FileNotFoundError:
                                await ctx.send("Oops, I couldn't find the image. Please check the file path.")
                                return
                    else:
                        await ctx.send(f"**{ctx.author.mention}**, ...Hey, I know things might feel overwhelming right now, but you're not alone. If you ever need someone to talk to, I'm here for you.")
                        
                        try:
                            msg = await self.bot.wait_for('message', timeout=30.0, check=lambda m: m.author == ctx.author)
                            if any(word in msg.content.lower() for word in ["thanks", "thank you", "thank"]):
                                await ctx.send("type shit")
                        except asyncio.TimeoutError:
                            pass
                        return 

                if bullets_in_chamber <= 0:
                    image_path = "reactions/Chiaki_Annoyed.png"
                    try:
                        await ctx.send(file=discord.File(image_path))
                    except FileNotFoundError:
                        await ctx.send("Oops, I couldn't find the image. Please check the file path.")
                    await ctx.send("What's the point of playing then, dummy!")
                    return

        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond!")
            return

        await ctx.send(f"Alright, {bullets_in_chamber} bullets in the chamber! *SPIN!*")

        # Corrected game logic: If the random number is within the bullet count, the player dies.
        result = random.randint(1, 6)

        if result <= bullets_in_chamber:
            await ctx.send(f"**{ctx.author.mention}**, *BANG!* Sayonara chief.")
        else:
            try:
                await ctx.send(f"**{ctx.author.mention}**, *click...* You're safe...for now")
                
                # Update balance for surviving the game
                await self.update_balance(ctx.author.id, ctx.guild.id, ctx.author.name, 100)
                
                # Fetch the updated balance
                current_balance = await self.get_balance(ctx.author.id, ctx.guild.id, ctx.author.name)
                
                if current_balance is not None:
                    await ctx.send(f"Congratulations {ctx.author.mention}, you survived! You've won 100 doubloons! 🎉 You now have {current_balance} doubloons.")
                else:
                    await ctx.send(f"Congratulations {ctx.author.mention}, you survived! You've won 100 doubloons! 🎉 (Economy system not available)")

            except Exception as e:
                await ctx.send(f"An error occurred: {e}")

            
    @commands.command(name="connect_four", aliases=["c4"], help="Play Connect 4 with a friend!")
    async def connect_four(self, ctx, opponent: discord.Member):
        if opponent == ctx.author:
            await ctx.send("You can't play against yourself!")
            return
        
        confirmation_message = await ctx.send(f"{opponent.mention}, do you accept the Connect Four challenge from {ctx.author.mention}? React with ✅ to accept or ❌ to decline.")

        await confirmation_message.add_reaction("✅")
        await confirmation_message.add_reaction("❌")

        def check(reaction, user):
            return user == opponent and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)

            if str(reaction.emoji) == "❌":
                await ctx.send(f"{opponent.mention} declined the challenge. Game canceled.")
                return

        except asyncio.TimeoutError:
            await ctx.send(f"{opponent.mention} didn't respond in time. Game canceled.")
            return

        board = [[self.empty_slot for _ in range(self.columns)] for _ in range(self.rows)]
        game_over = False
        turn = 0  # 0 = Player 1, 1 = Player 2
        players = [ctx.author, opponent]

        # Function to render the board as a message
        def render_board():
            return "\n".join(["".join(row) for row in board]) + "\n" + "".join(self.number_emojis)

        game_message = await ctx.send(f"{ctx.author.mention} vs {opponent.mention} - Connect Four!\n{render_board()}")

        # Add reaction numbers for column selection
        for emoji in self.number_emojis:
            await game_message.add_reaction(emoji)

        # Function to check if a player has won
        def check_win(piece):
            # Check horizontal, vertical, and diagonal connections
            for r in range(self.rows):
                for c in range(self.columns - 3):
                    if all(board[r][c + i] == piece for i in range(4)):
                        return True
            for r in range(self.rows - 3):
                for c in range(self.columns):
                    if all(board[r + i][c] == piece for i in range(4)):
                        return True
            for r in range(self.rows - 3):
                for c in range(self.columns - 3):
                    if all(board[r + i][c + i] == piece for i in range(4)):
                        return True
                    if all(board[r + 3 - i][c + i] == piece for i in range(4)):
                        return True
            return False

        # Game loop
        while not game_over:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add",
                    timeout=180,
                    check=lambda r, u: u == players[turn] and str(r.emoji) in self.number_emojis
                )

                column = self.number_emojis.index(str(reaction.emoji))

                # Remove player's reaction to keep the interface clean
                await game_message.remove_reaction(reaction.emoji, user)    

                # Find the lowest empty row in the selected column
                for row in reversed(range(self.rows)):
                    if board[row][column] == self.empty_slot:
                        board[row][column] = self.player_pieces[turn]
                        break
                else:
                    await ctx.send(f"{players[turn].mention}, that column is full! Choose another one.")
                    continue

                # Update board
                await game_message.edit(content=f"{players[0].mention} vs {players[1].mention} - Connect Four!\n{render_board()}")

                # Check if the current player won
                if check_win(self.player_pieces[turn]):
                    await ctx.send(f"🎉 {players[turn].mention} wins! 🎉")
                    game_over = True
                    return

                # Switch turn
                turn = 1 - turn

                await game_message.remove_reaction(reaction, players[turn])

            except asyncio.TimeoutError:
                await ctx.send("Game timed out! No move was made in time.")
                return
            
    @commands.command(name="free_for_all_russian_roulette", aliases=["f4rr"], help="Free-for-all Russian Roulette!")
    async def free_for_all_russian_roulette(self, ctx):
        """Free-for-all Russian Roulette where players can join and take turns firing!"""

        # Message to start joining phase
        join_message = await ctx.send("🔫 **Russian Roulette!** 🔫\nReact with ✅ to join! You have **30 seconds**.")

        await join_message.add_reaction("✅")

        # Collect players who react ✅
        players = []

        def join_check(reaction, user):
            return (
                user != self.bot.user
                and reaction.message.id == join_message.id
                and str(reaction.emoji) == "✅"
                and user not in players
            )

        try:
            while True:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=join_check)
                players.append(user)
        except asyncio.TimeoutError:
            pass  # Timeout ends joining phase

        if len(players) < 2:
            await ctx.send("Not enough players joined. Game canceled.")
            return

        # Confirm players
        player_mentions = ", ".join(player.mention for player in players)
        await ctx.send(f"🎲 Players: {player_mentions}\nLet's load the revolver!")

        # Set initial bullets
        bullets = 1
        minimum = 1
        round_number = 1

        while len(players) > 1:
            await ctx.send(f"🔄 *New Round {round_number}!* There is **{bullets} bullet{'s' if bullets > 1 else ''}** in the chamber.")

            # Player turn loop
            for player in players[:]:  # Iterate over a copy of the list
                # Ask the player if they want to increase bullet count
                bullet_message = await ctx.send(f"🎯 {player.mention}, it's your turn to fire. React with 🔼 to add a bullet (max 5).")

                await bullet_message.add_reaction("🔼")

                def bullet_check(reaction, user):
                    return user == player and str(reaction.emoji) == "🔼"

                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=5.0, check=bullet_check)
                    if bullets < 5:
                        bullets += 1
                        await ctx.send(f"🔫 {player.mention} added a bullet! There are now **{bullets} bullets**.")
                except asyncio.TimeoutError:
                    pass  # If they don't react, continue

                await asyncio.sleep(2)  # Pause for suspense

                # Fire the gun
                bullet_position = random.randint(1, 6)
                if bullet_position <= bullets:
                    await ctx.send(f"💥 **BANG!** {player.mention} is out of the game! 💀")
                    players.remove(player)
                    bullets = 1  # Reset bullets after a death
                    break
                else:
                    await ctx.send(f"🔫 *click...* {player.mention} survives!")

                await asyncio.sleep(2)

                if len(players) == 1:
                    break

            # Chiaki adds a bullet if the count is still at 1 at the start of a new round
            if bullets == minimum and round_number < 5:
                bullets += 1
                minimum = bullets
                await ctx.send(f"💜 Chiaki steps in and loads an extra bullet... There are now **{bullets} bullets**.")

            round_number += 1

        # Declare winner
        winner = players[0]
        await ctx.send(f"🏆 **{winner.mention} wins the Russian Roulette!** 🎉 They survived against all odds.")

        # Award 100 doubloons
        await self.update_balance(winner.id, 100)
        current_balance = await self.get_balance(winner.id)
        await ctx.send(f"💰 {winner.mention}, you won **100 doubloons!** You now have {current_balance} doubloons.")

class slot_machine_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.slot_symbols = ["🍒", "🍋", "🍇", "🍉", "🔔", "⭐"]
    
    async def get_balance(self, user_id):
        """Fetch the balance from the economy_cog."""
        economy_cog = self.bot.get_cog("economy_cog")
        return economy_cog.get_balance(user_id)

    async def update_balance(self, user_id, amount):
        """Update the balance in the economy_cog."""
        economy_cog = self.bot.get_cog("economy_cog")
        economy_cog.update_balance(user_id, amount)

    @commands.command(name="slot", aliases=['sm', 'slots'], help="Spin the slot machine!")
    async def slot(self, ctx):
        # Spin the slot machine by randomly choosing 3 symbols
        spin_result = [random.choice(self.slot_symbols) for _ in range(3)]
        result_message = " | ".join(spin_result)
        await ctx.send(f"**LET'S GO GAMBLING!!!**")
        
        # Check if the user wins (all 3 symbols match)
        if len(set(spin_result)) == 1:
            # User wins
            await ctx.send(f"🎰 **{ctx.author.mention} spun the slots!** 🎰\n{result_message}\n**You win!** 🎉")
            await self.update_balance(ctx.author.id, 1000)# Add 1000 doubloons
            current_balance = await self.get_balance(ctx.author.id)
            await ctx.send(f"{ctx.author.mention}, you now have {current_balance} doubloons!")
        else:
            await ctx.send(f"🎰 **{ctx.author.mention} spun the slots!** 🎰\n{result_message}\nAw dang it! Better luck next time! 😢")