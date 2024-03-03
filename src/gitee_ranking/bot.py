import time

import httpx
import rich

from gitee_ranking.model import Contributor, Repo, Token


class GiteeBot(object):
    def __init__(
        self, email: str, password: str, client_id: str, client_secret: str
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret

        token = self.init_access_token(email, password)
        self._access_token = token.access_token
        self.refresh_token = token.refresh_token
        self.expires_in = token.expires_in
        self.created_at = token.created_at

    @property
    def access_token(self) -> str:
        # 检查是否过期
        if int(time.time()) - self.created_at > self.expires_in:
            token = self.refresh_access_token()
            self._access_token = token.access_token
            self.refresh_token = token.refresh_token
            self.expires_in = token.expires_in
            self.created_at = token.created_at

        return self._access_token

    def init_access_token(self, email, password) -> Token:
        try:
            res = httpx.post(
                url="https://gitee.com/oauth/token",
                data={
                    "grant_type": "password",
                    "username": email,
                    "password": password,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": "user_info",
                },
                timeout=100,
            )
        except Exception as e:
            rich.print(e)
            raise e

        if res.status_code != 200:
            print(res.json())
            raise Exception("Failed to init access token")

        return Token(**res.json())

    def refresh_access_token(self) -> Token:
        try:
            res = httpx.post(
                url="https://gitee.com/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                },
                timeout=100,
            )
        except Exception as e:
            rich.print(e)
            raise e

        if res.status_code != 200:
            rich.print(res.json())
            raise Exception("Failed to refresh access token")

        return Token(**res.json())

    def get_repo_info(self, owner: str, repo: str) -> Repo:
        """获取仓库的信息"""

        print("Start getting repo info: {owner}/{repo}".format(owner=owner, repo=repo))

        contributors = self.get_repo_contributors(owner, repo)
        _repo = Repo(
            issues_count=self.get_repo_item_count(owner, repo, "issues"),
            prs_count=self.get_repo_item_count(owner, repo, "pulls", {"state": "all"}),
            commits_count=self.get_repo_item_count(
                owner, repo, "commits", {"since": "2024-02-27"}
            ),
            contributors_count=len(contributors),
            contributors=contributors,
        )

        print("Finish getting repo info: {owner}/{repo}".format(owner=owner, repo=repo))

        return _repo

    def get_repo_item_count(
        self, owner: str, repo: str, item: str, params: dict = {}
    ) -> int:
        """获取仓库的某项数量"""

        if item not in ["issues", "pulls", "contributors", "commits"]:
            rich.print(
                "item must be one of ['issues', 'pulls', 'contributors', 'commits']"
            )
            return 0

        # 注意分页
        item_count = 0
        while True:
            try:
                _params = {
                    "page": item_count // 30 + 1,
                    "per_page": 30,
                }
                _params.update(params)
                res = httpx.get(
                    f"https://gitee.com/api/v5/repos/{owner}/{repo}/{item}",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    params=_params,
                    timeout=100,
                )
            except Exception as e:
                rich.print(e)
                return 0

            if res.status_code != 200:
                rich.print(res.json())
                return 0

            items = res.json()
            item_count += len(items)

            if len(items) < 30:
                break

        # rich.print(f"Get {item} count: {item_count} for {owner}/{repo}")
        return item_count

    def get_repo_contributors(self, owner: str, repo: str) -> list[Contributor]:
        """获取仓库的贡献者"""

        contributors = []
        try:
            res = httpx.get(
                f"https://gitee.com/api/v5/repos/{owner}/{repo}/contributors",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=100,
            )
        except Exception as e:
            rich.print(e)
            return []

        if res.status_code != 200:
            rich.print(res.json())
            return []

        for item in res.json():
            new_contributor = Contributor(email=item.get("email", ""))
            contributors.append(new_contributor)

        return contributors
