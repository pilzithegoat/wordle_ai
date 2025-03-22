import discord
from discord import app_commands
from database import Session, Word, Game
from dotenv import load_dotenv
import os
import random
from datetime import datetime

load_dotenv()

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def get_daily_word():
    session = Session()
    daily_word = session.query(Word).filter_by(is_daily=True).first()
    session.close()
    return daily_word.word if daily_word else None

@client.event
async def on_ready():
    await tree.sync()
    print(f'Eingeloggt als {client.user}')

@tree.command(name="play", description="Starte ein neues Wordle-Spiel")
async def play(interaction: discord.Interaction):
    session = Session()
    user_id = str(interaction.user.id)
    
    # Check existing game
    existing_game = session.query(Game).get(user_id)
    if existing_game:
        session.close()
        return await interaction.response.send_message("Du hast bereits ein laufendes Spiel!", ephemeral=True)
    
    # Get daily word
    target_word = get_daily_word()
    if not target_word:
        target_word = random.choice(session.query(Word).all()).word
    
    # Create new game
    new_game = Game(
        user_id=user_id,
        target_word=target_word,
        attempts="",
        remaining_guesses="⬛⬛⬛⬛⬛\n"*6
    )
    
    session.add(new_game)
    session.commit()
    session.close()
    
    await interaction.response.send_message(f"Neues Wordle-Spiel gestartet! Du hast 6 Versuche.\n{new_game.remaining_guesses}")

@tree.command(name="guess", description="Mache einen Rateversuch")
async def guess(interaction: discord.Interaction, word: str):
    word = word.lower()
    session = Session()
    user_id = str(interaction.user.id)
    
    game = session.query(Game).get(user_id)
    if not game:
        session.close()
        return await interaction.response.send_message("Starte zuerst ein Spiel mit /play!", ephemeral=True)
    
    if len(word) != 5:
        session.close()
        return await interaction.response.send_message("Das Wort muss 5 Buchstaben lang sein!", ephemeral=True)
    
    # Check if word exists
    valid_word = session.query(Word).filter_by(word=word).first()
    if not valid_word:
        session.close()
        return await interaction.response.send_message("Ungültiges Wort!", ephemeral=True)
    
    # Process guess
    result = []
    target = game.target_word
    for i, letter in enumerate(word):
        if letter == target[i]:
            result.append("🟩")
        elif letter in target:
            result.append("🟨")
        else:
            result.append("⬛")
    
    result_str = "".join(result)
    game.attempts += result_str + "\n"
    remaining = game.remaining_guesses.split("\n")
    remaining[len(game.attempts.split("\n"))-1] = result_str
    game.remaining_guesses = "\n".join(remaining)
    
    if word == target:
        session.delete(game)
        session.commit()
        session.close()
        return await interaction.response.send_message(f"Gewonnen! 🎉\n{game.remaining_guesses}")
    
    if len(game.attempts.split("\n")) >= 6:
        session.delete(game)
        session.commit()
        session.close()
        return await interaction.response.send_message(f"Verloren! 😞 Das Wort war: {target}\n{game.remaining_guesses}")
    
    session.commit()
    session.close()
    await interaction.response.send_message(f"Versuche übrig: {6 - len(game.attempts.split('\n'))}\n{game.remaining_guesses}")

client.run(os.getenv('DISCORD_TOKEN'))
