import discord
from discord.ext import commands
import chess
import chess.svg
import chess.engine
from PIL import Image
import io
import cairosvg

# Path to Stockfish engine (ensure it's installed and set up correctly)
STOCKFISH_PATH = "C:\\Users\\Santiago\\Downloads\\stockfish\\stockfish-windows-x86-64-avx2.exe"

class ChessCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}  # Store ongoing games with user IDs as keys

    def generate_board_image(self, board):
        """Generate a PNG image of the chessboard using Pillow."""
        svg_board = chess.svg.board(board=board)
        
        # Convert SVG to PNG using cairosvg
        output = io.BytesIO()
        cairosvg.svg2png(bytestring=svg_board.encode('utf-8'), write_to=output)
        output.seek(0)
        
        return output

    async def send_board(self, ctx, board):
        """Send the current board state as an image."""
        image = self.generate_board_image(board)
        file = discord.File(image, filename="board.png")
        await ctx.send(file=file)

    async def update_game_status(self, ctx, game):
        """Update the game status after a move."""
        if game['board'].is_game_over():
            await self.send_game_result(ctx, game)
        else:
            await self.send_board(ctx, game['board'])

    async def send_game_result(self, ctx, game):
        """Send the result of the game."""
        if game['board'].is_checkmate():
            winner = self.bot.get_user(game['opponent']) if game['board'].turn else ctx.author
            await ctx.send(f"Game over! {winner.mention} wins by checkmate.")
        elif game['board'].is_stalemate():
            await ctx.send("Game over! It's a stalemate.")
        elif game['board'].is_insufficient_material():
            await ctx.send("Game over! Insufficient material for checkmate.")
        elif game['board'].is_seventyfive_moves():
            await ctx.send("Game over! 75-move rule reached.")
        elif game['board'].is_variant_draw():
            await ctx.send("Game over! Draw by variant rule.")
        del self.games[ctx.author.id]  # Remove game from active games

    @commands.command()
    async def start(self, ctx, opponent: discord.Member = None):
        """Start a new chess game against another user or the bot."""
        if ctx.author.id in self.games:
            await ctx.send("You're already in a game!")
            return
        
        board = chess.Board()
        if opponent and opponent != ctx.author:
            self.games[ctx.author.id] = {'board': board, 'opponent': opponent.id}
            self.games[opponent.id] = {'board': board, 'opponent': ctx.author.id}
            await ctx.send(f"Game started between {ctx.author.mention} and {opponent.mention}!")
        else:
            self.games[ctx.author.id] = {'board': board, 'bot': True, 'difficulty': 1}
            await ctx.send("Game started against the bot! Use `!difficulty <1-5>` to set difficulty.")
        
        await self.send_board(ctx, board)

    @commands.command()
    async def difficulty(self, ctx, level: int):
        """Set difficulty for Stockfish (1-5)."""
        if ctx.author.id not in self.games or 'bot' not in self.games[ctx.author.id]:
            await ctx.send("You're not playing against the bot!")
            return
        
        if 1 <= level <= 5:
            self.games[ctx.author.id]['difficulty'] = level
            await ctx.send(f"Difficulty set to {level}.")
        else:
            await ctx.send("Please choose a difficulty between 1 and 5.")

    @commands.command()
    async def move(self, ctx, move: str):
        """Make a move in an ongoing chess game."""
        if ctx.author.id not in self.games:
            await ctx.send("You're not in a game!")
            return

        game = self.games[ctx.author.id]
        board = game['board']
        
        try:
            chess_move = chess.Move.from_uci(move)
            if chess_move in board.legal_moves:
                board.push(chess_move)
            else:
                await ctx.send("Illegal move. Try again.")
                return
        except:
            await ctx.send("Invalid move format. Use UCI notation (e.g., e2e4).")
            return

        await self.update_game_status(ctx, game)

        if 'bot' in game:
            await self.bot_move(ctx, board, game['difficulty'])
        else:
            opponent_id = game['opponent']
            opponent = self.bot.get_user(opponent_id)
            await ctx.send(f"It's {opponent.mention}'s turn!")

    async def bot_move(self, ctx, board, difficulty):
        """Make a move using Stockfish."""
        skill_levels = {1: 4, 2: 9, 3: 14, 4: 19, 5: 20}
        try:
            # Use synchronous context manager for Stockfish engine
            with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
                engine.configure({'Skill Level': skill_levels[difficulty]})
                result = engine.play(board, chess.engine.Limit(time=1.0))
                board.push(result.move)
        except Exception as e:
            ctx.send(f"Error with Stockfish engine: {str(e)}")
            return

        await self.update_game_status(ctx, {'board': board, 'bot': True, 'difficulty': difficulty})
        await ctx.send("It's your turn!")

    @commands.command()
    async def resign(self, ctx):
        """Resign from an ongoing chess game."""
        if ctx.author.id in self.games:
            del self.games[ctx.author.id]
            await ctx.send("You resigned. Game over.")
        else:
            await ctx.send("You're not in a game.")
