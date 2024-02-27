import time

import schedule

from gitee_ranking.bot import GiteeBot
from gitee_ranking.config import settings
from gitee_ranking.lark import build_card, push_webhook
from gitee_ranking.model import Group

bot = GiteeBot(
    email=settings.email,
    password=settings.password,
    client_id=settings.client_id,
    client_secret=settings.client_secret,
)

with open(settings.group_csv, "r") as f:
    group_list = [
        Group(
            name=line.split(",")[0],
            owner=line.split(",")[1],
            repo=line.split(",")[2],
            url=line.split(",")[3],
        )
        for line in f.readlines()
    ]


def run_bot():
    print(
        "Running bot at {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    )
    card = build_card(group_list, bot)
    push_webhook(settings.webhook_url, card)
    print(
        "Bot finished at {}".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        )
    )


def app():
    schedule.every().day.at("20:00").do(run_bot)
    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    app()
