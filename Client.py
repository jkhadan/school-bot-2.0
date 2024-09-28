from discord import User
from discord.ext.commands import Bot
import numpy as np
import datetime as dt

from School import School


class Client:
    num_users = 0

    def __init__(self, user: User, school: School, unpacking: bool = False,
                 schedule: np.ndarray = None, homework: np.ndarray = None, inform_interval: int = None,
                 double_lab: np.ndarray = None):
        self.user = user
        self._school = school
        if not unpacking:
            self.schedule = np.zeros(school.periods, dtype=object)
            self.schedule.fill("Not yet set")
            self.homework = np.zeros(school.periods + 1, dtype=list)
            self.homework.fill([])
            self.inform_interval = dt.timedelta(minutes=5)
            self.double_lab = np.zeros(3, dtype=object)
            self.num_users += 1
        else:
            self.schedule = schedule
            self.homework = homework
            self.inform_interval = inform_interval
            self.double_lab = double_lab

    def add_period(self, numPeriod, period):
        self.schedule[numPeriod - 1] = period

    def del_period(self, period):
        self.schedule[period] = "Not yet set"

    def add_homework(self, period, homework):
        self.homework[period] = homework

    def set_double_lab(self, letter_day: str, science_block: int, gym_block: int):
        self.double_lab[0] = letter_day
        self.double_lab[1] = science_block
        self.double_lab[2] = gym_block

    def as_dict(self) -> dict:
        """
        :return: A dictionary containing the object attributes used to store the object in a json file
        """
        dictObject = dict()
        dictObject["user"] = self.user.id
        dictObject["schedule"] = str(self.schedule)
        dictObject["homework"] = str(self.homework)
        dictObject["inform interval"] = int(self.inform_interval.total_seconds() // 60)
        dictObject["double lab"] = str(self.double_lab)

        return dictObject

    @classmethod
    def remove_user(cls):
        cls.num_users -= 1


def unpack_json(json_dictionary: dict, bot: Bot, school: School):
    user = bot.get_user(int(json_dictionary["user"]))
    print(int(json_dictionary["user"]))
    schedule = np.asarray(json_dictionary["schedule"].split(' '), dtype=object)
    homework = np.asarray(json_dictionary["homework"].split(' '), dtype=list)
    inform_interval = int(json_dictionary["inform interval"])
    double_lab = np.asarray(json_dictionary["double lab"].split(' '), dtype=object)

    return Client(user=user, school=school, unpacking=True, schedule=schedule,
                  homework=homework, inform_interval=inform_interval, double_lab=double_lab)
