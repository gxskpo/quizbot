from discord.ext import commands
import discord
from utils import DataBase
import random
import asyncio


class ReplyButtons(discord.ui.View):
    def __init__(self, answers, correct_answer: str = None):
        super().__init__()
        self.correct_answer = correct_answer
        self.answers = answers
        self.a.label = answers[0]
        self.b.label = answers[1]
        self.c.label = answers[2]
        print([i for i in self.children])

    @discord.ui.button(label="A", style=discord.ButtonStyle.gray)
    async def a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._callback(interaction, button)

    @discord.ui.button(label="B", style=discord.ButtonStyle.gray)
    async def b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._callback(interaction, button)

    @discord.ui.button(label="C", style=discord.ButtonStyle.gray)
    async def c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._callback(interaction, button)

    async def _callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        for i in self.children:
            i.disabled = True

        if str(button.label) == self.correct_answer:
            embed = discord.Embed(color=0x9af180)
            embed.title = "Correcto!"
            button.style = discord.ButtonStyle.green
            await interaction.response.edit_message(view=self, embed=embed)
        else:
            embed = discord.Embed(color=0xf15b72)
            embed.title = "Incorrecto!"
            button.style = discord.ButtonStyle.red
            await interaction.response.edit_message(view=self, embed=embed)


class SelectQuiz(discord.ui.Select):
    def __init__(self, quizzes):
        options = []
        self.quizzes = quizzes
        for quiz in quizzes:
            options.append(discord.SelectOption(label=quiz[2], description=quiz[3], value=str(quiz[0])))
        super().__init__(placeholder="Selecciona un quiz", options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(color=0xF1D3DE)
        selected = int(self.values[0]) - 1
        quiz_data = self.quizzes[selected]
        embed.title = quiz_data[2] + ":"
        embed.description = quiz_data[3]
        randomized_quiz_data = random.sample(quiz_data[4:], len(quiz_data[4:]))
        view = ReplyButtons(randomized_quiz_data, quiz_data[4])
        await interaction.response.edit_message(embed=embed, view=view, content='')


class Quizzes(commands.GroupCog, group_name="quiz"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = DataBase("quizzes.db")
        self.db.execute(self.create_table)

    create_table = """
    CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    question TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    wrong_answer1 TEXT NOT NULL,
    wrong_answer2 TEXT NOT NULL
    );
    """

    async def wait_for_message(self, ctx: commands.Context, message_content: str):
        await ctx.send(message_content)
        while 1:
            try:
                msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout=60.0)
                if msg.content.lower() == "cancel":
                    await ctx.send("Cancelando...")
                    raise ZeroDivisionError()
                return msg.content
            except asyncio.TimeoutError:
                await ctx.send("Tiempo de espera agotado")
                raise ZeroDivisionError()

    @commands.hybrid_command(name="create", description="Crea un nuevo quiz")
    async def create_quizz(self, ctx: commands.Context):
        try:
            guild_id = ctx.guild.id
            category = await self.wait_for_message(ctx, "Ingresa la categoría")
            question = await self.wait_for_message(ctx, "Ingresa la pregunta")
            correct_answer = await self.wait_for_message(ctx, "Ingresa la respuesta correcta")
            wrong_answer1 = await self.wait_for_message(ctx, "Ingresa una respuesta incorrecta")
            wrong_answer2 = await self.wait_for_message(ctx, "Ingresa otra respuesta incorrecta")
            query = f"""
            INSERT INTO quizzes 
            (guild_id, category, question, correct_answer, wrong_answer1, wrong_answer2)
            VALUES
            (?, ?, ?, ?, ? ,?)
            """
            self.db.execute(query, (guild_id, category, question, correct_answer, wrong_answer1, wrong_answer2))
            await ctx.send("Quiz creado!")
        except ZeroDivisionError:
            return ctx.send("Comando cancelado!")

    @commands.hybrid_command(name="quiz", description="Responde un quiz")
    async def answer_quiz(self, ctx: commands.Context):
        quizz = self.db.read(f"SELECT * FROM quizzes WHERE guild_id = {ctx.guild.id} OR guild_id = 0")
        if not quizz:
            return await ctx.send("No hay quizzes disponibles")
        view = discord.ui.View()
        view.add_item(SelectQuiz(quizz))
        await ctx.send("Selecciona un quiz", view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Quizzes(bot))
