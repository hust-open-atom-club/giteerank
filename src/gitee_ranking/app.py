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

group_list = [
    Group(
        owner="hustsecurity",
        repo="hust-detours",
        name="A",
        url="https://gitee.com/hustsecurity/hust-detours",
    ),
    Group(
        owner="hustsecurity",
        repo="hust-detours",
        name="B",
        url="https://gitee.com/hustsecurity/hust-detours",
    ),
]

card = build_card(group_list, bot)

push_webhook(settings.webhook_url, card)
