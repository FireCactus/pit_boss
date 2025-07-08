from typing import *
from asyncio import *
import time
from croniter import croniter
from datetime import datetime

'''
A ClockEvent is one that triggers once per day,week,every other day etc.
They are triggered at creation unless enabled is set to False.
If recuriing is True, then the event will keep activating in the background
'''

class ClockEvent():
    def __init__(self, cron_string: str, action: Callable[[], None], recurring: bool = True, enabled: bool = True) -> None:
        assert croniter.is_valid(cron_string), "Invalid CRON string"

        self.cron_string: str = cron_string
        self.action: Callable[[], None] = action
        self.recurring: bool = recurring
        self.enabled: bool = enabled
        self.running: bool = False
        self.last_action_time: Optional[float] = None

        if self.enabled:
            self.running = True
            create_task(self.trigger())

    def get_status(self) -> str:
        if self.enabled: 
            return "Active" 
        else: 
            return "Disabled"

    def enable(self) -> None:
        self.enabled = True
        if self.running == False:
            self.running = True
            create_task(self.trigger())

    def disable(self) -> None:
        self.enabled = False

    async def trigger(self) -> None:
        iter = croniter(self.cron_string, datetime.now())

        while self.enabled:
            next_time = iter.get_next(datetime)
            delay = (next_time - datetime.now()).total_seconds()

            if delay > 0:
                await sleep(delay)

            if self.enabled == False:
                break

            self.last_action_time = time.time()
            self.action()

            if self.recurring == False:
                break

        self.running = False


    


    
