from typing import *
from asyncio import *
import time

'''
A timed event is one that triggers after x amount of seconds.
They are triggered at creation unless enabled is set to False.
If recuriing is True, then the event will keep activating in the background
'''


class TimedEvent():
    def __init__(self, reactivation_time: int, action: Callable[[], None], recurring: bool = True, enabled: bool = True) -> None:
        
        assert reactivation_time > 0, "Error while creating TimedEvent!\nreactivation time must be at least 1s"
        
        self.reactivation_time: int = reactivation_time
        self.recurring: bool = recurring
        self.action: Callable[[], None] = action
        self.enabled: bool = enabled
        self.running: bool = False
        
        self.last_action_time: Optional[int] = None
        
        if self.enabled:
            create_task(self.trigger())  # Fire-and-forget the trigger as background task

    def get_status(self) -> str:
        if self.enabled:
            return "Active"
        else:
            return "Disabled"

    def enable(self) -> None:
        self.enabled = True
        if self.running == False:
            self.running = True  # Race condition fix
            create_task(self.trigger())
    
    def disable(self) -> None:
        self.enabled = False

    async def trigger(self) -> None:
        self.running = True
        while self.enabled:
            await sleep(self.reactivation_time)
            if self.enabled:
                self.last_action_time = time.time()
                self.action()
            else:
                self.running = False
                break

            if self.recurring == False:
                self.running = False
                break



    


    
