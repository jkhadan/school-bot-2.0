import datetime as dt
from typing import List


class School:
    def __init__(self, name: str, times: List[dt.time], periods: int = 7, downtime: int = 7, lunch_down_time: int = 35,
                 period_before_lunch: int = 3):
        self.downtime = dt.timedelta(minutes=downtime)
        self._name = name
        self.times = times
        self.periods = periods

    def get_num_blocks(self):
        return len(self.times)

    def as_dict(self) -> dict:
        packaged_dict: dict = dict()

        packaged_dict["name"] = self._name
        packaged_dict["downtime"] = int(self.downtime.total_seconds() // 60)
        str_time_list: List[str] = [time.strftime("%H:%M") for time in self.times]
        packaged_dict["times"] = str_time_list
        packaged_dict["periods"] = self.periods

        return packaged_dict