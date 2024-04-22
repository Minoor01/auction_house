import schedule
import time
from django.utils import timezone
from .views import past_auction_items

def schedule_past_auction_items():
    current_time = timezone.now()
    past_auction_items(None) 
    print("Task completed.")
    
schedule.every().minute.do(schedule_past_auction_items)


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
