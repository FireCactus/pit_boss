from schedule.ClockEvent import ClockEvent
from database.PlayersDatabase import PlayersDatabase
db = PlayersDatabase()


# Renew daily reward for all players at midnight
daily_renewal_event = ClockEvent("0 0 * * *", db.renew_daily_for_all)

