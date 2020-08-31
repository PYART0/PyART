from __future__ import print_function
from __future__ import division

import calendar
from datetime import datetime
import pytz
import time


def pretty_date_time(date_time):
    now = datetime.now(pytz.utc)
    if type(date_time) is int:
        reveal_type(datetime)