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

file_list = settings.groups_str.split(",")


def run_bot():
    current_hour = time.localtime().tm_hour
    if (
        current_hour >= settings.start_hour
        and current_hour < settings.start_hour + len(file_list) * 2
    ):
        group_list = []
        with open(
            file_list[(current_hour - settings.start_hour) % len(file_list)], "r"
        ) as f:
            group_list.extend(
                [
                    Group(
                        name=line.split(",")[0],
                        owner=line.split(",")[1],
                        repo=line.split(",")[2],
                        url=line.split(",")[3],
                    )
                    for line in f.readlines()
                ]
            )
    else:
        print(
            "Not in the time range. Current time: {}".format(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            )
        )
        return

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
    print("Starting bot")
    schedule.every().hour.do(run_bot)
    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    app()
