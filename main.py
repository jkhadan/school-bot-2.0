import json
import discord
import datetime as dt
import torch

from pytz import timezone
from discord.ext import commands
from asyncio import sleep
from typing import List
from random import choice

from Client import Client
from SchedulingHHS import SchedulingHHS
from School import School
from model import NeuralNet
from nltk_utils import tokenize, bag_of_words

# Discord Bot Initialization
intent = discord.Intents(messages=True, members=True, guilds=True)

bot = commands.Bot(command_prefix="$", intents=intent)

school = School("Howell High School",
                [dt.time(hour=7, minute=30), dt.time(hour=8, minute=42), dt.time(hour=9, minute=54),
                 dt.time(hour=11, minute=47), dt.time(hour=12, minute=59)])

# A.I. Chat Bot initialization
with open('intents.json', 'r') as b:
    intents = json.load(b)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

data = torch.load("data.pth")

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()
greetings = ["Why Hello there", "Greetings!", "How do you do?", "Hello!", "Hey there!", "Hi!"]

# Load Data
users = {}

# with open("UserData.json", 'r') as UD:
#     user_data = json.load(UD)
#
# for data in user_data["users"]:
#     users[data["user"]] = unpack_json(data, bot, school)


@bot.event
async def on_ready():
    print("School Bot is now Ready")


@bot.command()
async def register(ctx):
    if ctx.message.author.id not in users.keys():
        users[ctx.message.author.id] = Client(ctx.message.author, school)
        await ctx.send(f"Thank you for joining the School Bot Network!")
        server = bot.get_channel(842425967594045521)
        await ctx.send("To start using the bot, please refer to the list of available commands below, and ask about "
                       "these topics!")
        await server.send(f"{ctx.message.author.mention} has joined the School Bot Network!")
        # with open("UserData.json", 'r') as y:
        #     obj = json.load(y)
        #
        # obj["users"] = users
        #
        # with open("UserData.json", "a") as f:
        #     users.get(ctx.message.author.id).as_dict()
    else:
        await ctx.send("You are already registered to the School Bot Network.")


@bot.command()
async def debug():
    print(users)


@bot.command()
async def unregister(ctx):
    if ctx.message.author.id in users.keys():
        users.pop(ctx.message.author.id)
        # with open("UserData.json", "r") as r:
        #     file = json.load(r)
        #     for user in file["users"]:
        #         if file["user"] == ctx.message.author.id:
        #             file.pop(file["user"])
        #             break

        Client.remove_user()
        await ctx.send("Success! You have successful been unregistered from School Bot!")
    else:
        await ctx.send("You aren\'t registered. In order to register, use $register.")


@bot.command(pass_context=True)
async def setperiod(ctx, *arg):
    if ctx.message.author.id in users.keys() and 0 < int(arg[0]) <= school.periods:
        period = ""
        for part in arg[1:]:
            period += part + " "

        if len(period) == 0:
            await ctx.send("You need to put something")
            return None

        period = period[0:len(period) - 1]

        users.get(ctx.message.author.id).add_period(int(arg[0]), period)
        await ctx.send(f"Success! Period {int(arg[0])} has been set to {period}!")

    else:
        await ctx.send("You must be registered using $register in order to interact with school bot")


@bot.command()
async def events(ctx):
    # if ctx.message.author.id in users.keys():
    if SchedulingHHS.check_if_school_today() is not False:
        embed = discord.Embed(
            title="Events",
            description="Here are the events scheduled for today",
            color=discord.Color.from_rgb(46, 48, 146)
        )

        for event in range(len(SchedulingHHS.check_if_school_today()[1])):
            embed.add_field(name=f"Event {event}", value=SchedulingHHS.check_if_school_today()[1][event])

        ctx.send(embed=embed)


@bot.command()
async def daysleft(ctx):
    end_day = dt.date(month=6, day=23, year=2021)
    current = SchedulingHHS.current.date()
    delta = end_day - current

    await ctx.send(f"There are {delta} days remaining in school")
    # Count number of cycles left by counting number of G Days
    # Count number of school days by counting number of letter days


@bot.command()
async def changeinterval(ctx, arg):
    if ctx.message.author.id in users.keys():
        if int(arg) < 30:
            users[ctx.message.author.id].inform_interval = dt.timedelta(minutes=int(arg))
            await ctx.send(f"Success! You will now be informed {arg} minutes prior to an event")
        else:
            await ctx.send("Please enter a number that is less than 30")
    else:
        await ctx.send("You must be registered using $register in order to interact with school bot")


@bot.command()
async def periods(ctx):
    if ctx.message.author.id in users.keys():

        schedule_layout = discord.Embed(
            description=ctx.message.author.mention,
            color=discord.Colour.from_rgb(46, 48, 146)
        )
        schedule_layout.set_author(name=f"{ctx.message.author.name}'s schedule", icon_url=ctx.message.author.avatar_url)

        for i in range(school.periods):
            schedule_layout.add_field(name=f"Period {i + 1}", value=users.get(ctx.message.author.id).schedule[i],
                                     inline=False)

        await ctx.send("Here are your periods!", embed=schedule_layout)

    else:
        await ctx.send("You must be registered using $register in order to interact with school bot")


@bot.event
async def on_message(message):
    if message.content.startswith("$"):
        await bot.process_commands(message)
    elif not message.author.bot:
        if message.author.id in users.keys():
            if message.guild is None:
                process = tokenize(message.content)
                bag = bag_of_words(process, all_words)
                bag = bag.reshape(1, bag.shape[0])
                bag = torch.from_numpy(bag).to(device)

                output = model(bag).to(device)
                _, predicted = torch.max(output, dim=1)
                tag = tags[predicted.item()]

                confidence = torch.softmax(output, dim=1)
                conf = confidence[0][predicted.item()]

                if conf.item() > 0.75:
                    for intend in intents["intents"]:
                        if tag == intend["tag"]:
                            if intend["response"] == "greet":
                                await message.author.send(choice(greetings))
                            elif intend["response"] == "timeleft":
                                await timeleft(message.author)
                            elif intend["response"] == "schedule":
                                await schedule(message.author)
                            elif intend["response"] == "periods":
                                await periods(message.author)
                            elif intend["response"] == "event":
                                await events(message.author)
                            elif intend["response"] == "daysleft":
                                await daysleft(message.author)
                else:
                    await message.author.send("Sorry, doesn't look like I know that one yet.")
        else:
            await message.author.send("Sorry, you must be registered with School Bot in order to interact with it.")


@bot.command(pass_context=True)
async def schedule(ctx, arg=None):
    # if ctx.message.author.id in users.keys():
    if arg is None:
        # Set to see schedule for other days (maybe day of the week, or key phrases such as tomorrow, then loop
        # through day until its that day)
        temp = SchedulingHHS.get_day_schedule(users.get(ctx.author.id))

        view = discord.Embed(
            description=ctx.author.mention,
            color=discord.Color.from_rgb(46, 48, 146)
        )

        view.set_author(
            name=f"{ctx.author.name}\'s {SchedulingHHS.check_if_school_today()[0]} Day Schedule",
            icon_url=ctx.author.avatar_url)

    else:
        try:
            argument = str(arg)

            numID = int(argument[3:len(argument) - 1])
            user = await bot.fetch_user(numID)

            temp = SchedulingHHS.get_day_schedule(users.get(numID))

            view = discord.Embed(
                description=user.mention,
                color=discord.Color.from_rgb(46, 48, 146)
            )

            view.set_author(
                name=f"{user.name}'s {SchedulingHHS.check_if_school_today()[0]} Day Schedule",
                icon_url=user.avatar_url)

        except:
            await ctx.send("Please either mention the user you want to view, or put nothing to view your own")
            return None

    for i in range(school.get_num_blocks()):
        view.add_field(name=f"Block {i + 1}", value=temp[i], inline=False)
        print(temp[i])

    await ctx.send("Here is your schedule for today!", embed=view)

    # else:
    #     ctx.send("You must be in the School Bot Network in order to interact with it.")


def get_block_duration():
    if SchedulingHHS.check_if_school_today() is not False:
        # Block Duration Calculation
        total_minutes = abs(((school.times[1].hour * 60) + school.times[1].minute) - (
                (school.times[0].hour * 60) + school.times[0].minute)) - int(
            (school.downtime.total_seconds() // 60))

        hours = 0
        for i in range(1, total_minutes + 1):
            if i % 60 == 0:
                hours += 1

        # Block Duration Time Delta
        minutes = total_minutes % 60

        return minutes, hours

    else:
        return False


def get_end_times() -> List[dt.time]:
    blocks = []
    delta = dt.timedelta(hours=get_block_duration()[1], minutes=get_block_duration()[0])
    date = SchedulingHHS.current.date()
    for i in range(school.get_num_blocks()):
        time = dt.time(hour=school.times[i].hour, minute=school.times[i].minute)
        datetime_holder = dt.datetime.combine(date, time)
        final_end_time = datetime_holder + delta
        blocks.append(final_end_time.time())

    return blocks


@bot.command()
async def timeleft(ctx):
    # if ctx.message.author.id in users.keys():
    if SchedulingHHS.check_if_school_today() is not False:

        # Current Time Today
        current = SchedulingHHS.current.time()
        blocks = get_end_times()

        if blocks[0] < current < blocks[1] or blocks[1] < current < blocks[2] or \
                blocks[2] < current < blocks[3] or blocks[3] < current < blocks[4]:
            await ctx.send("Looks like you\'re not currently in class. This command is only to be used in class.")
            return None

        count = 0
        for j in range(school.get_num_blocks()):
            if current < blocks[j]:
                subtract = dt.datetime.combine(SchedulingHHS.current, blocks[j])
                current_time_subtractable = dt.datetime.combine(SchedulingHHS.current, current)
                delta = subtract - current_time_subtractable
                await ctx.send(
                    f"There are {(delta.total_seconds() // 60) + (get_block_duration()[1] * 60)} minutes"
                    f" and {delta.total_seconds() % 60:.2f} seconds left in Block {j + 1}")
                count += 1
                break
        if count == 0:
            await ctx.send("Looks like you\'re not currently in class. This command is only to be used in class.")

    else:
        await ctx.send("Looks like you\'re not currently in class. This command is only to be used in class.")
    # else:
    #     await ctx.send("Sorry, but you must be apart of the School Bot Network in order to use this feature.")


@bot.command(pass_context=True)
async def addhw(ctx, due_date, reminder_time, *arg):
    if ctx.message.author.id in users.keys():
        # MM/DD
        try:
            reminder_datetime = dt.datetime.strptime(due_date + " " + reminder_time, "%d/%m %H:%M")

        except ValueError:
            await ctx.send("Error: Incorrect date input, please enter the date the homework is due and the time you "
                           "would like to be reminded of it. Ex. $addhw ")
            return None

        # Build Homework String
        hw = ""
        for arg in arg:
            hw += arg + " "

        hw = hw[:len(hw) - 1]

        # Find Current Block

        if SchedulingHHS.check_if_school_today() is not False:
            current = SchedulingHHS.current.time()
            blocks = get_end_times()
            block = school.periods

            if not current < school.times[0]:
                for i in range(school.get_num_blocks()):
                    if current < blocks[i]:
                        block = i
                        break

            ctx.send(f"Success! {hw} has been assigned to block {block} due {due_date}")
            users.get(ctx.message.author.id).homework[block].append((homework, reminder_datetime))

            # Later create another session loop to loop through user homework and notify them at the times desired.


@bot.command()
async def homework(ctx):
    if ctx.message.author.id in users.keys():
        embed = discord.Embed(
            title="Homework",
            description="Here is your homework schedule!"
        )
        block = 1

        for hw in users.get(ctx.message.author.id).homework:
            embed.add_field(name=f"{block}", value=f"{hw}")
            block += 1

        await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def doublelab(ctx, letter_day, science_block, gym_block):
    if ctx.message.author.id in users.keys():
        users.get(ctx.message.author.id).set_double_lab(letter_day, int(science_block), int(gym_block))


async def session():
    await bot.wait_until_ready()

    while not bot.is_closed():
        if SchedulingHHS.check_if_school_today() is not False:
            currentUpdatable = dt.datetime.now().astimezone(timezone("US/Eastern"))
            for i in range(school.get_num_blocks()):
                for user in users.values():
                    if currentUpdatable.time().hour == school.times[i].hour:
                        if SchedulingHHS.get_day_schedule(user)[i] != "Not yet set":
                            if currentUpdatable.time().minute == (
                                    school.times[i].minute - (user.inform_interval.total_seconds() // 60)):
                                embed = discord.Embed(
                                    title=f"Get Ready for {SchedulingHHS.get_day_schedule(user)[i]}!",
                                    description=f"Block {i + 1} will begin in {user.inform_interval} minutes!",
                                    color=discord.Color.from_rgb(46, 48, 146)
                                )
                                try:
                                    await user.user.send(embed=embed)
                                except (discord.errors.Forbidden, discord.HTTPException):
                                    pass

                            if currentUpdatable.time().minute == school.times[i].minute:
                                embed = discord.Embed(
                                    title=f"Time for {SchedulingHHS.get_day_schedule(user)[i]}!",
                                    description=f"{SchedulingHHS.get_day_schedule(user)[i]} has now begun",
                                    color=discord.Color.from_rgb(46, 48, 146)
                                )

                                embed.add_field(name="Time span",
                                                value=f"This block will run from "
                                                      f"{school.times[i]} to {get_end_times()[i]}",
                                                inline=True)

                                try:
                                    await user.user.send(embed=embed)
                                except (discord.errors.Forbidden, discord.HTTPException):
                                    pass

                    if currentUpdatable.time().hour == int(get_end_times()[i].hour - get_block_duration()[
                        1]) and currentUpdatable.time().minute == int(
                        get_end_times()[i].minute - (user.inform_interval.total_seconds() // 60)):
                        embed = discord.Embed(
                            title=f"Almost there {user.user.name}!",
                            description=f"Only {user.inform_interval} minutes left in "
                                        f"{SchedulingHHS.get_day_schedule(user)[i]}!",
                            color=discord.Color.from_rgb(46, 48, 146)
                        )

                        try:
                            await user.user.send(embed=embed)
                        except (discord.errors.Forbidden, discord.HTTPException):
                            pass

        await sleep(45)


# async def save():
#     await bot.wait_until_ready()
#     file_user_dict = {
#         "users": []
#     }
#
#     while not bot.is_closed():
#         with open("UserData.json", 'wt') as file:
#             file.write("")
#             for user in users.values():
#                 file_user_dict["users"].append(user.as_dict())
#             json.dump(file_user_dict, file, indent=2)
#
#         print("Save Complete!")
#
#         await sleep(30)


bot.loop.create_task(session())
# bot.loop.create_task(save())
bot.run("API Key Goes Here")
