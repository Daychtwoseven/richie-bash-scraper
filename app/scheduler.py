from apscheduler.schedulers.background import BackgroundScheduler
from update_data import UpdateData


def start(action):
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_all, 'interval', minutes=600)
    scheduler.start()


def run_all():
    UpdateData()