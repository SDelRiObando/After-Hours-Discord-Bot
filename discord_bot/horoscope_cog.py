import sqlite3
import discord
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from discord.ext import commands
from datetime import datetime

class HoroscopeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_name = 'horoscope.db'

        # Initialize the database
        self.create_table()

    def create_table(self):
        """Create the horoscope_data table if it doesn't exist"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Create table if it doesn't exist with a single DATE column
        c.execute('''CREATE TABLE IF NOT EXISTS horoscope_data (
                        user_id INTEGER,
                        guild_id INTEGER,
                        username TEXT NOT NULL,
                        birth_date DATE NOT NULL,
                        birth_time TEXT,
                        birth_place TEXT,
                        PRIMARY KEY (user_id, guild_id)
                    )''')
        conn.commit()
        conn.close()

    @commands.command()
    async def set_birthday(self, ctx, birth_date: str):
        """Store the user's birth date in the database (in MM/DD/YYYY format for birth_date)"""
        user_id = ctx.author.id
        guild_id = ctx.guild.id
        username = ctx.author.name

        # Try to parse the birth_date in MM/DD/YYYY format
        try:
            birth_date_obj = datetime.strptime(birth_date, "%m/%d/%Y")
            birth_date_str = birth_date_obj.date()  # Extract the date as YYYY-MM-DD format
        except ValueError:
            await ctx.send("Invalid date format! Please use MM/DD/YYYY.")
            return

        # Insert or update the user's birth data in the database (only birth_date here)
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        c.execute('''
        INSERT OR REPLACE INTO horoscope_data (user_id, guild_id, username, birth_date)
        VALUES (?, ?, ?, ?)
        ''', (user_id, guild_id, username, birth_date_str))

        conn.commit()
        conn.close()

        await ctx.send(f"Your birth date has been saved! {ctx.author.mention}")

    @commands.command()
    async def set_time(self, ctx, *, birth_time: str):
        """Store the user's birth time in the database"""
        user_id = ctx.author.id
        guild_id = ctx.guild.id

        # Insert or update the user's birth time in the database
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        c.execute('''
        UPDATE horoscope_data SET birth_time = ? WHERE user_id = ? AND guild_id = ?
        ''', (birth_time, user_id, guild_id))

        conn.commit()
        conn.close()

        await ctx.send(f"Your birth time has been saved as {birth_time}! {ctx.author.mention}")

    @commands.command()
    async def set_place(self, ctx, *, birth_place: str):
        """Store the user's birth place in the database"""
        user_id = ctx.author.id
        guild_id = ctx.guild.id

        # Insert or update the user's birth place in the database
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        c.execute('''
        UPDATE horoscope_data SET birth_place = ? WHERE user_id = ? AND guild_id = ?
        ''', (birth_place, user_id, guild_id))

        conn.commit()
        conn.close()

        await ctx.send(f"Your birth place has been saved as {birth_place}! {ctx.author.mention}")

    @commands.command()
    async def get_birthday(self, ctx):
        """Retrieve the stored birth details for the user"""
        user_id = ctx.author.id
        guild_id = ctx.guild.id

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        c.execute('''
        SELECT birth_date, birth_time, birth_place FROM horoscope_data WHERE user_id = ? AND guild_id = ?
        ''', (user_id, guild_id))

        result = c.fetchone()
        conn.close()

        if result:
            birth_date, time, place = result
            birth_date_str = birth_date.strftime("%d/%m/%Y")  # Format the date as DD/MM/YYYY
            await ctx.send(f"{ctx.author.mention}, your birth details are:\n"
                           f"Date of Birth: {birth_date_str}\n"
                           f"Time: {time}\n"
                           f"Place: {place}")
        else:
            await ctx.send(f"{ctx.author.mention}, you have not set your birth details yet. Use `!!set_birthday` to set it.")

    @commands.command()
    async def zodiac(self, ctx):
        """Tell the user their zodiac sign based on their birthday"""
        user_id = ctx.author.id
        guild_id = ctx.guild.id

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        c.execute('''
        SELECT birth_date FROM horoscope_data WHERE user_id = ? AND guild_id = ?
        ''', (user_id, guild_id))

        result = c.fetchone()
        conn.close()

        if result:
            birth_date = result[0]
            try:
                # Convert the birth_date string back to a datetime object
                birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d")
                zodiac_sign = self.get_zodiac_sign(birth_date_obj)
            except ValueError:
                zodiac_sign = "Unknown"
            await ctx.send(f"{ctx.author.mention}, your zodiac sign is **{zodiac_sign}**!")
        else:
            await ctx.send(f"{ctx.author.mention}, you have not set your birth details yet. Use `!!set_birthday` to set it.")
        
    @commands.command()
    async def fortune(self, ctx, period: str):
        """Fetches and sends the user's fortune based on their zodiac sign for the given period."""
        user_id = ctx.author.id
        guild_id = ctx.guild.id
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        c.execute('''
        SELECT birth_date FROM horoscope_data WHERE user_id = ? AND guild_id = ?
        ''', (user_id, guild_id))

        result = c.fetchone()
        conn.close()

        if result:
            birth_date = result[0]
            try:
                # Convert the birth_date string back to a datetime object
                birth_date_obj = datetime.strptime(birth_date, "%Y-%m-%d")
                zodiac_sign = self.get_zodiac_sign(birth_date_obj)
            except ValueError:
                zodiac_sign = "Unknown"
        else:
            zodiac_sign = None

        if not zodiac_sign:
            await ctx.send("Please set your zodiac sign first using `!set_birthday`.")
            return
        
        # Handle different periods: daily, weekly, or monthly
        if period.lower() == "daily":
            horoscope = await self.get_horoscope_from_api(zodiac_sign)
            if horoscope:
                await ctx.send(f"Your daily horoscope for {zodiac_sign.capitalize()}:\n{horoscope}")
            else:
                await ctx.send("Sorry, I couldn't fetch your daily horoscope at the moment.")
        elif period.lower() == "weekly" or period.lower() == "monthly":
            await ctx.send(f"The {period.lower()} horoscope is coming soon! Stay tuned.")
        else:
            await ctx.send("Invalid period. Please specify `daily`, `weekly`, or `monthly`.")

    def get_zodiac_sign(self, birth_date):
        """Determine the zodiac sign based on the user's birth date"""
        month = birth_date.month
        day = birth_date.day

        # Zodiac date ranges
        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return "Aries"
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return "Taurus"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            return "Gemini"
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            return "Cancer"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return "Leo"
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return "Virgo"
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            return "Libra"
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            return "Scorpio"
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            return "Sagittarius"
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return "Capricorn"
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return "Aquarius"
        else:
            return "Pisces"    
    
    async def get_horoscope_from_api(self, zodiac_sign):
        """Fetch daily horoscope for the given zodiac sign by scraping the website."""
        # Zodiac sign numbers (for horoscope.com)
        zodiac_numbers = {
            "aries": 1, "taurus": 2, "gemini": 3, "cancer": 4,
            "leo": 5, "virgo": 6, "libra": 7, "scorpio": 8,
            "sagittarius": 9, "capricorn": 10, "aquarius": 11, "pisces": 12
        }
        
        # Use the number corresponding to the zodiac sign
        zodiac_number = zodiac_numbers.get(zodiac_sign.lower())
        if not zodiac_number:
            return None

        # URL for fetching the horoscope
        url = f"https://www.horoscope.com/us/horoscopes/general/horoscope-general-daily-today.aspx?sign={zodiac_number}"

        try:
            # Send a GET request to fetch the page
            response = requests.get(url)
            if response.status_code != 200:
                return None

            # Parse the page content with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the horoscope text inside the main-horoscope div
            horoscope_div = soup.find('div', class_='main-horoscope')
            if horoscope_div:
                # Get the specific <p> tag containing the horoscope
                horoscope_paragraph = horoscope_div.find('p')
                if horoscope_paragraph:
                    # Return the text of the paragraph (strip to remove unnecessary whitespace)
                    return horoscope_paragraph.get_text(strip=True)
                else:
                    return None
            else:
                return None

        except Exception as e:
            print(f"Error fetching horoscope: {e}")
            return None