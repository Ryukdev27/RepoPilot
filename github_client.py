import os
from os import path
from certifi import contents
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

        response = requests.get(
            url,
            headers=self.headers
        )

        response.raise_for_status()

        return response.json()

    def get_issue(self, owner, repo, issue_number):
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"

        response = requests.get(
            url,
            headers=self.headers
        )

        response.raise_for_status()

        return response.json()

    def get_file(self, owner, repo, path):
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

        response = requests.get(
            url,
            headers=self.headers
        )

        response.raise_for_status()

        return response.json()
    
    def list_files(self, owner: str, repo: str, path: str = ""):
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        response = requests.get(
            url,
            headers=self.headers
        )
        response.raise_for_status()
        contents = response.json()
        files = []
        for item in contents:
            files.append({
                "name": item["name"],
                "path": item["path"],
                "type": item["type"],
            })
        return files

    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = None,
    ):
        repository = self.get_repository(owner, repo)

        if base is None:
            base = repository.default_branch

        pr = repository.create_pull(
            title=title,
            body=body,
            head=head,
            base=base,
        )

        return {
            "number": pr.number,
            "url": pr.html_url,
            "title": pr.title,
    }