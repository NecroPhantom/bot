import discord
from discord.ext import commands
import asyncio

# Initialize the bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
leaderboard = {}

# Command to view the leaderboard
@bot.tree.command(name="leaderboard", description="View the leaderboard.")
async def leaderboard_cmd(interaction: discord.Interaction):
    leaderboard_sorted = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    embed = discord.Embed(title="Leaderboard", color=discord.Color.blue())
    
    if not leaderboard_sorted:
        await interaction.response.send_message("Leaderboard is empty!")
        return

    page = 1
    entries_per_page = 10
    max_pages = (len(leaderboard_sorted) + entries_per_page - 1) // entries_per_page

    def generate_page(page):
        start = (page - 1) * entries_per_page
        end = start + entries_per_page
        page_entries = leaderboard_sorted[start:end]
        
        leaderboard_text = ""
        for idx, (user_id, score) in enumerate(page_entries, start=start+1):
            user = bot.get_user(user_id)
            leaderboard_text += f"{idx}. {user.display_name if user else 'Unknown'} - {score} points\n"
        
        embed.clear_fields()
        embed.add_field(name="Position", value=leaderboard_text, inline=False)
        embed.set_footer(text=f"Page {page} of {max_pages}")
        return embed

    embed = generate_page(page)
    message = await interaction.response.send_message(embed=embed)

    # Adding reactions for paging if there are multiple pages
    if max_pages > 1:
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        # Check for reactions
        def check(reaction, user):
            return user == interaction.user and reaction.message.id == message.id and reaction.emoji in ["⬅️", "➡️"]

        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
                if reaction.emoji == "⬅️" and page > 1:
                    page -= 1
                elif reaction.emoji == "➡️" and page < max_pages:
                    page += 1
                embed = generate_page(page)
                await message.edit(embed=embed)
                await message.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                break

# Command to add score
@bot.tree.command(name="aura", description="Add score to a user")
async def aura(interaction: discord.Interaction, option: str, score: int, tag: discord.Member):
    if option == "add":
        if tag.id not in leaderboard:
            leaderboard[tag.id] = 0
        leaderboard[tag.id] += score
        await interaction.response.send_message(f"Added {score} points to {tag.display_name}. They now have {leaderboard[tag.id]} points!")
    else:
        await interaction.response.send_message("Invalid option! Use '/aura add <score> <@user>' to add points.")

# Bot event to run on startup
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# Run the bot (replace TOKEN with your actual bot token)
bot.run('')
