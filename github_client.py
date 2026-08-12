import os
from dotenv import load_dotenv
import requests

load_dotenv()


class GitHubClient:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")

        if not self.token:
            raise ValueError("GITHUB_TOKEN is not set")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def get_repository(self, owner, repo):
        url = f"https://api.github.com/repos/{owner}/{repo}"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()