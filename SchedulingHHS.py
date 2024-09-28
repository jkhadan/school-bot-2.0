import datetime as dt
import pytz
import icalendar as ical
import numpy as np

from Client import Client


class SchedulingHHS:
    current = dt.datetime.now().astimezone(pytz.timezone("US/Eastern"))
    with open("SWCal.ics", 'rb') as f:
        calendar = ical.Calendar.from_ical(f.read())

    @classmethod
    def check_if_school_today(cls):
        letterDay = ""
        events = []

        if 1 <= cls.current.isoweekday() < 6:
            for component in cls.calendar.walk():
                if component.name == "VEVENT":
                    if component.get("dtstart").dt == cls.current.date():
                        if "Day: Block Schedule" in component.get("summary"):
                            letterDay = component.get("summary")[0]
                        else:
                            events.append(component.get("summary"))

        return False if letterDay == "" else letterDay, events

    @classmethod
    def get_day_schedule(cls, user: Client):
        day_schedule = np.zeros(5, dtype=object)
        school_check = cls.check_if_school_today()

        if school_check[0] == 'A':
            day_schedule[0] = user.schedule[0]
            day_schedule[1] = user.schedule[1]
            day_schedule[2] = user.schedule[2]
            day_schedule[3] = user.schedule[4]
            day_schedule[4] = user.schedule[5]

        elif school_check[0] == 'B':
            day_schedule[0] = user.schedule[3]
            day_schedule[1] = user.schedule[0]
            day_schedule[2] = user.schedule[1]
            day_schedule[3] = user.schedule[6]
            day_schedule[4] = user.schedule[4]

        elif school_check[0] == 'C':
            day_schedule[0] = user.schedule[2]
            day_schedule[1] = user.schedule[3]
            day_schedule[2] = user.schedule[0]
            day_schedule[3] = user.schedule[5]
            day_schedule[4] = user.schedule[6]

        elif school_check[0] == 'D':
            day_schedule[0] = user.schedule[1]
            day_schedule[1] = user.schedule[2]
            day_schedule[2] = user.schedule[3]
            day_schedule[3] = user.schedule[4]
            day_schedule[4] = user.schedule[5]

        elif school_check[0] == 'E':
            day_schedule[0] = user.schedule[0]
            day_schedule[1] = user.schedule[1]
            day_schedule[2] = user.schedule[2]
            day_schedule[3] = user.schedule[6]
            day_schedule[4] = user.schedule[4]

        elif school_check[0] == 'F':
            day_schedule[0] = user.schedule[3]
            day_schedule[1] = user.schedule[0]
            day_schedule[2] = user.schedule[1]
            day_schedule[3] = user.schedule[5]
            day_schedule[4] = user.schedule[6]

        elif school_check[0] == 'G':
            day_schedule[0] = user.schedule[2]
            day_schedule[1] = user.schedule[3]
            day_schedule[2] = user.schedule[6]
            day_schedule[3] = user.schedule[4]
            day_schedule[4] = user.schedule[5]

        if school_check[0] == user.double_lab[0]:
            day_schedule[user.double_lab[2]] = day_schedule[user.double_lab[1]]

        return day_schedule
