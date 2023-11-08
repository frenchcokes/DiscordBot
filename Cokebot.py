import os
from dotenv import load_dotenv
import discord
import mysql.connector
from discord.ext import commands

load_dotenv()
#DATABASE
db = mysql.connector.connect(
      user = os.getenv("user"),
      password = os.getenv("password"),
      host = os.getenv("host"),
	  database = os.getenv("database")
)
cursor = db.cursor()

#CODE
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix='?', intents=intents)

@bot.event
async def on_ready():
	guild_count = 0

	for guild in bot.guilds:
		print(f"- {guild.id} (name: {guild.name})")

		guild_count = guild_count + 1

	print("OkaygeBot is in " + str(guild_count) + " guilds.")

@bot.command()
async def why(ctx):
	helpString = "Hello! I am OkaygeBot. I track how your honor scores. To thank someone for their help, react to their message with a 🫡. I will add to their score to track that they are truly a MAN/WOMAN of the people!"
	await ctx.send(helpString)

@bot.command()
async def commandlist(ctx):
	output = "?commandlist - Command list\n" + "?why - General information\n" + "?honorrank - Displays top ranking users\n" + "?honorscore (username) - Shows honor score of user (username is not the same as display name) "
		  
	await ctx.send(output)

@bot.command()
async def honorrank(ctx):
	query = f"CREATE TABLE IF NOT EXISTS USERDATA (DISPLAYNAME VARCHAR(255), NAME VARCHAR(255), SCORE INT);"
	cursor.execute(query)

	query = "SELECT * FROM USERDATA ORDER BY SCORE DESC LIMIT 5;"
	cursor.execute(query)
	result = cursor.fetchall()

	outputString = "TOP MEN/WOMEN OF THE PEOPLE\n"
	counter = 1
	for row in result:
		outputString = outputString + str(counter) + ". " + row[0] + " - " + str(row[2]) + " 🫡\n"
		counter = counter + 1

	await ctx.send(outputString)

@bot.command()
async def honorscore(ctx, arg = ""):
	query = f"CREATE TABLE IF NOT EXISTS USERDATA (DISPLAYNAME VARCHAR(255), NAME VARCHAR(255), SCORE INT);"
	cursor.execute(query)

	query = f"SELECT * FROM USERDATA WHERE NAME = \"{arg}\""
	cursor.execute(query)
	result = cursor.fetchall()

	if(len(result) >= 1):
		result = result[0]
		await ctx.send(str(result[0]) + " - " + str(result[2]) + " 🫡")	
	else:
		await ctx.message.add_reaction("👎")

@bot.event
async def on_reaction_add(reaction, user):
	query = f"CREATE TABLE IF NOT EXISTS USERDATA (DISPLAYNAME VARCHAR(255), NAME VARCHAR(255), SCORE INT);"
	cursor.execute(query)

	if(reaction.emoji == "🫡"):
		
		await reaction.message.add_reaction("👍")
		query = f"SELECT EXISTS(SELECT * FROM USERDATA WHERE NAME = \"{reaction.message.author.name}\" )"
		cursor.execute(query)
		result = cursor.fetchone()[0]
		
		if(str(result) == "0"):	
			query = f"INSERT INTO USERDATA (DISPLAYNAME,NAME,SCORE) VALUES (\"{reaction.message.author.display_name}\",\"{reaction.message.author.name}\",{1})"
			cursor.execute(query)
		else:
			query = f"UPDATE USERDATA SET SCORE = SCORE + 1 WHERE NAME = \"{reaction.message.author.name}\"; "
			cursor.execute(query)

			updateQuery = f"UPDATE USERDATA SET DISPLAYNAME = \"{reaction.message.author.display_name}\" WHERE NAME = \"{reaction.message.author.name}\"; "
			cursor.execute(updateQuery)

		db.commit()

@bot.event
async def on_reaction_remove(reaction, user):

	if(reaction.emoji == "🫡"):
		query = f"SELECT EXISTS(SELECT * FROM USERDATA WHERE NAME = \"{reaction.message.author.name}\" )"
		cursor.execute(query)
		result = cursor.fetchone()[0]

		if(str(result) == "0"):	
			query = f"INSERT INTO USERDATA (DISPLAYNAME,NAME,SCORE) VALUES (\"{reaction.message.author.display_name}\",\"{reaction.message.author.name}\",{0})"
			cursor.execute(query)
		else:
			query = f"UPDATE USERDATA SET SCORE = SCORE - 1 WHERE NAME = \"{reaction.message.author.name}\" "
			cursor.execute(query)
			updateQuery = f"UPDATE USERDATA SET DISPLAYNAME = \"{reaction.message.author.display_name}\" WHERE NAME = \"{reaction.message.author.name}\"; "
			print(updateQuery)
			cursor.execute(updateQuery)

		db.commit()

@bot.event
async def on_message(message):
	if(message.author.bot == False):
		if (("sadge" in message.content.lower()) == True):
			await message.add_reaction("😥")
		elif(("okayge" in message.content.lower()) == True):
			await message.add_reaction("😃")
		elif(("gmnz" in message.content.lower()) == True):
			await message.add_reaction("🇬")
			await message.add_reaction("🇲")
			await message.add_reaction("🇳")
			await message.add_reaction("🇿")
		else:
			await bot.process_commands(message)
	

bot.run(os.getenv("botToken"))