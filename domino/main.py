import sqlite3
import discord
from secret import TOKEN, ADMINS
from discord.ext import commands

from util import calculate_points, generate_html
from solution_cache import SolutionCache
from player_cache import PlayerCache
from task_cache import TaskCache


def reset():
    pass


bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

solutions = SolutionCache()
players = PlayerCache()
tasks = TaskCache()

ADMIN_COMMANDS = [
    "!registered",
    "!banned",
    "!finish",
    "!newtasks",
    "!gettasks",
    "!changetour",
    "!res_res_res",
    "!super_res",
]


@bot.check
def dm_only(ctx):
    return ctx.guild is None


@bot.check
def special_commands_only_for_admins(ctx):
    command = str(ctx.message.content).strip().split(maxsplit=1)[0]
    if command in ADMIN_COMMANDS:
        return ctx.author.id in ADMINS
    return True


################################### АДМИН КОМАНДЫ


@bot.command(
    name="newtasks",
    help="загрузить новые задачи: Турнир Число1 Число2 ответ, где Число1 и Число2 - числа на доминошке",
)
async def newtasks(ctx):
    print(ctx.author.id, ctx.author.name, ctx.message.content)
    parts = ctx.message.content.strip().split(maxsplit=4)[1:]
    if len(parts) < 4:
        ok, msg = False, "Недостаточно параметров"
        print(msg)
        await ctx.send(msg)
    else:
        ok, msg = tasks.create_or_update_task(*parts)
        print(msg)
        await ctx.send(msg)


# отладочная команда
@bot.command(name="gettasks", help="получить задачи: Турнир Число1 Число2")
async def gettasks(ctx):
    print(ctx.author.id, ctx.author.name, ctx.message.content)
    parts = ctx.message.content.strip().split(maxsplit=4)[1:]
    if len(parts) < 3:
        ok, msg = False, "Недостаточно параметров"
        print(msg)
        await ctx.send(msg)
    else:
        num1, num2 = int(parts[1]), int(parts[2])
        if num1 > num2:
            num1, num2 = num2, num1
        ok, msg = True, str(tasks.tours[parts[0]][(num1, num2)])
        print(msg)
        await ctx.send(msg)


@bot.command(name="finish", help="Сдампить базу. Теперь можно убить бота")
async def finish(ctx):
    print(ctx.author.id, ctx.author.name, ctx.message.content)
    solutions.conn.close()
    players.conn.close()
    tasks.conn.close()
    await ctx.send("Сдамплена база. Теперь можно убить бота")


@bot.command(name="res_res_res", help="Сгенерировать табличку результатов")
async def res_res_res(ctx):
    print(ctx.author.id, ctx.author.name, ctx.message.content)
    generate_html(solutions, tasks, players)
    await ctx.send("Сгенерены html-ки")


################################### ИГРОВОЙ ПРОЦЕСС
@bot.command(name="solve", help='Отправить решение в виде "solve Число1 Число2 ОТВЕТ"')
async def solve(ctx):
    print(ctx.author.id, ctx.author.name, ctx.message.content)
    parts = ctx.message.content.strip().split(maxsplit=3)[1:]
    if len(parts) < 3:
        msg = "Недостаточно параметров"
        print(msg)
        await ctx.send(msg)
        return
    if not players.players_storage[str(ctx.author.id)].allowed:
        msg = "Вы еще не зарегистрированы"
        print(msg)
        await ctx.send(msg)
        return
    tour = players.players_storage[str(ctx.author.id)].tour
    ok_, msgg = tasks.is_task(tour, *parts)
    if not ok_:
        await ctx.send(msgg)
        return
    # проверить, что не было повторной посылки по той же задаче
    # solution is [user_id, name, answer, time] where name is num1num2
    count = 0
    num1, num2 = int(parts[0]), int(parts[1])
    if num1 > num2:
        num1, num2 = num2, num1
    for sol in solutions.solution_storage:
        if sol[0] == str(ctx.author.id) and sol[1] == str(num1) + str(num2):
            count += 1
    if num1 == 0 and num2 == 0 and count == 1:
        await ctx.send("Задачу 0 0 можно сдавать только один раз")
        return
    elif count == 1 and tasks.check_task(tour, num1, num2, parts[2]):
        await ctx.send("Вы уже отправили верное решение по этой доминошке")
        return
    elif count == 2:
        await ctx.send("Вы не можете сдавать доминошку более 2х раз")
        return

    ok, msg1 = solutions.new_solution(str(ctx.author.id), *parts)
    print(msg1)
    ok2 = tasks.check_task(tour, *parts)
    await ctx.send(
        msg1 + "\n" + "Ура! ответ совпал с текущим в базе"
        if ok2
        else "Увы, ответ не совпал с текущим в базе"
    )


@bot.command(name="points", help="Число очков команды")
async def points(ctx):
    print(ctx.author.id, ctx.author.name, ctx.message.content)
    if not players.players_storage[str(ctx.author.id)].allowed:
        msg = "Вы еще не зарегистрированы"
        print(msg)
        await ctx.send(msg)
        return
    tour = players.players_storage[str(ctx.author.id)].tour
    ok, msg = calculate_points(str(ctx.author.id), tour, solutions, tasks)
    print(msg)
    await ctx.send(msg)


@bot.command(name="fio", help="Зарегистрировать ФИО")
async def fio(ctx):
    print(ctx.author.id, ctx.author.name, ctx.message.content)
    parts = ctx.message.content.strip().split(maxsplit=1)[1:]
    if len(parts) == 0:
        msg = "Недостаточно параметров"
        print(msg)
        await ctx.send(msg)
        return
    ok, msg = players.set_fio(str(ctx.author.id), parts[0])
    print(msg)
    await ctx.send(msg)


@bot.command(name="tour", help="Зарегистрировать Турнир")
async def tour(ctx):
    print(ctx.author.id, ctx.author.name, ctx.message.content)
    parts = ctx.message.content.strip().split(maxsplit=1)[1:]
    if len(parts) == 0:
        msg = "Недостаточно параметров"
        print(msg)
        await ctx.send(msg)
        return
    ok, msg = players.set_tour(str(ctx.author.id), parts[0])
    print(msg)
    await ctx.send(msg)


@bot.command(name="register", help="Отправить Анкету на проверку")
async def register(ctx):
    print(ctx.author.id, ctx.author.name, ctx.message.content)
    ok, msg_user, msg_admin = players.set_fixed(str(ctx.author.id))
    players.allow(str(ctx.author.id), "burat")
    print(msg_user + "\n" + msg_admin)
    await ctx.send(msg_user)


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


@bot.event
async def on_message(msg):
    if msg.guild is not None and msg.content.startswith("!"):
        await msg.delete()
        return
    await bot.process_commands(msg)


def main():
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
