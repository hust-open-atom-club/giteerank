import time

import schedule

from gitee_ranking.bot import GiteeBot
from gitee_ranking.config import settings
from gitee_ranking.lark import build_card, push_webhook
from gitee_ranking.model import Contributor, Group
from gitee_ranking.schema import Class, ClassMember
from gitee_ranking.schema import Group as _Group
from gitee_ranking.schema import Log, SessionLocal

bot = GiteeBot(
    email=settings.email,
    password=settings.password,
    client_id=settings.client_id,
    client_secret=settings.client_secret,
)


def run_bot():
    current_hour = time.localtime().tm_hour
    # current_hour = 9  # DEBUG

    title = ""
    groups = []
    group_list = []

    session = SessionLocal()

    if current_hour >= settings.start_hour and current_hour < settings.end_hour:
        # 获取按照 id 排序的所有 class 列表
        classes = session.query(Class).order_by(Class.id).all()
        if not classes:
            print("No classes found")
            return

        # 查询 log，获取上一次查询的班级
        last_class_index = -1
        last_log = session.query(Log).order_by(Log.id.desc()).first()

        if last_log is not None:
            last_class = (
                session.query(Class).filter(Class.id == last_log.class_id).first()
            )

            # 在 classes 中查找 last_log 的索引
            for i, class_ in enumerate(classes):
                if class_.id == last_class.id:
                    last_class_index = i
                    break

        if last_class_index == len(classes) - 1:
            last_class_index = -1
            print("Enter next loop")

        # last_class_index = 1 # DEBUG
        title = classes[last_class_index + 1].name
        groups = (
            session.query(_Group)
            .filter(_Group.class_id == classes[last_class_index + 1].id)
            .all()
        )

        # 写入一条log
        new_log = Log(class_id=classes[last_class_index + 1].id)
        session.add(new_log)
        session.commit()

    elif current_hour == settings.end_hour or current_hour == settings.start_hour - 1:
        title = "汇总"
        groups = session.query(_Group).all()

    else:
        print(
            "Not in the time range. Current time: {}".format(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            )
        )
        return

    if not groups:
        print("No groups found")
        return

    for group in groups:
        contributors = session.query(ClassMember).filter(
            ClassMember.group_id == group.id
        )
        if not contributors:
            print("No contributors found for group {} {}".format(group.name, group.id))
            continue

        class_ = session.query(Class).filter(Class.id == group.class_id).first()

        group_list.append(
            Group(
                name=group.name,
                owner=group.repo_url.split("/")[-2],
                repo=group.repo_url.split("/")[-1],
                url=group.repo_url,
                class_name=class_.name,
                authors=[
                    Contributor(name=member.name, email=member.email)
                    for member in contributors
                ],
            )
        )

    session.close()

    print(
        "Running bot at {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    )

    # 构建和发送卡片
    card = build_card(title, group_list, bot)
    push_webhook(settings.webhook_url, card)

    print(
        "Bot finished at {}".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        )
    )


def app():
    print("Starting bot")
    print("Webhook url: {}".format(settings.webhook_url))
    schedule.every().hour.do(run_bot)
    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    app()
