import json
import time

import httpx

from gitee_ranking.bot import GiteeBot
from gitee_ranking.model import Group

card_template = """{{
  "elements": [
    {{
      "tag": "column_set",
      "flex_mode": "none",
      "background_style": "default",
      "columns": [
        {{
          "tag": "column",
          "width": "weighted",
          "weight": 4,
          "vertical_align": "top",
          "elements": [
          {group_cards}
          ]
        }}
      ]
    }},
    {{
      "tag": "note",
      "elements": [
        {{
          "tag": "img",
          "img_key": "img_v3_028f_c81e21a5-b997-487c-a38d-7d46a6a904ag",
          "alt": {{
            "tag": "plain_text",
            "content": ""
          }}
        }},
        {{
          "tag": "plain_text",
          "content": "Gitee Watcher"
        }}
      ]
    }}
  ],
  "header": {{
    "template": "orange",
    "title": {{
      "content": "{date} HustDetour {title}",
      "tag": "plain_text"
    }}
  }}
}}
"""

group_element_template = """{{
  "tag": "markdown",
  "content": "**Group {group_name} | {class_name} | **[{owner}/{repo}]({repo_url})"
}},
{{
  "tag": "column_set",
  "flex_mode": "none",
  "background_style": "grey",
  "columns": [
    {{
      "tag": "column",
      "width": "weighted",
      "weight": 1,
      "vertical_align": "top",
      "elements": [
        {{
          "tag": "markdown",
          "content": "**<font color='red'>{commits_count}</font>**\\n<font color='grey'>Commits</font>\\n**<font color='red'>{issues_count}</font>**\\n<font color='grey'>Open Issues</font>",
          "text_align": "center"
        }}
      ]
    }},
    {{
      "tag": "column",
      "width": "weighted",
      "weight": 1,
      "vertical_align": "top",
      "elements": [
        {{
          "tag": "markdown",
          "content": "**<font color='red'>{prs_count}</font>**\\n<font color='grey'>Open PRs</font>\\n**<font color='red'>{contributors_count}</font>**\\n<font color='grey'>Contributors</font>",
          "text_align": "center"
        }}
      ]
    }},
    {{
      "tag": "column",
      "width": "weighted",
      "weight": 2,
      "vertical_align": "top",
      "elements": [
        {{
          "tag": "markdown",
          "content": "{contributors}\\n<font color='grey'>Contributors</font>",
          "text_align": "center"
        }}
      ]
    }}
  ]
}},"""


def push_webhook(webhook_url: str, card: list | dict) -> None:
    """推送消息到 webhook"""
    with httpx.Client(
        timeout=100,
    ) as client:
        res = client.post(webhook_url, json={"msg_type": "interactive", "card": card})

    if res.status_code != 200:
        print(res.json())
        raise Exception(f"Failed to push webhook: {res.text}")

    code = res.json()["code"]
    if code != 0:
        print(res.json())
        raise Exception(f"Failed to push webhook: {res.text}")


# NOTE: 修改后的 group_list 是从数据库中读取出来的
def build_card(title: str, group_list: list[Group], bot: GiteeBot) -> dict | list:
    """构建卡片"""
    group_cards = ""
    for group in group_list:
        repo_info = bot.get_repo_info(group.owner, group.repo)

        contributors: list[str] = []

        black_list = [
            "noreply@github.com",
            "dtarditi@microsoft.com",
            "b.gianfo@gmail.com",
            "aukinros@microsoft.com",
            "jaykrell@ntdev.microsoft.com",
            "noreply@gitee.com",
            "bgianf@microsoft.com",
            "ofekshilon@gmail.com",
            "galenh@microsoft.com",
        ]

        # 这里的 contributor 只有 email
        email_list = [((author.email).strip()).lower() for author in group.authors]
        contributor_name_list = [author.name for author in group.authors]
        for contributor in repo_info.contributors:
            if contributor.email in black_list:
                continue

            if contributor.email in email_list:
                contributors.insert(
                    0, contributor_name_list[email_list.index(contributor.email)]
                )
                continue

            contributors.append(contributor.email)

        group_cards += group_element_template.format(
            owner=group.owner,
            repo=group.repo,
            repo_url=group.url,
            group_name=group.name,
            class_name=group.class_name,
            commits_count=repo_info.commits_count,
            issues_count=repo_info.issues_count,
            prs_count=repo_info.prs_count,
            contributors_count=len(contributors),
            contributors="\\n".join(contributors),
        )

    group_cards = group_cards[:-1]  # 去除最后一个逗号

    _card = card_template.format(
        title=title,
        group_cards=group_cards,
        date=time.strftime("%Y-%m-%d", time.localtime()),
    )

    card = json.loads(_card.replace("\n", ""))
    return card
