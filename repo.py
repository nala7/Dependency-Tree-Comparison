import requests
import base64
import os
import subprocess


class Repo:
    def __init__(self, name, url_path, github_token):
        self.name = name
        self.url_path = url_path
        self.is_gradle = False
        self.is_pom = False
        self.api_url = None
        self.headers = {"Authorization": github_token}
        self.config_file = None
        self.local_repo_dir = os.path.join(os.getcwd(), self.name)
        self.graph_generated = False
        self.json_generated = False

        try:
            repo_parts = self.url_path.rstrip('/').split('/')
            owner, repo = repo_parts[-2], repo_parts[-1]
            self.api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        except (IndexError, ValueError):
            raise ValueError("Invalid GitHub repository URL.")

        self._clone_repo()

    def _clone_repo(self):
        if not self.api_url:
            raise ValueError("API URL is not set. Ensure the repository URL is valid.")

        response = requests.get(self.api_url, headers=self.headers)
        if response.status_code == 200:
            contents = response.json()
            for item in contents:
                if item['type'] == 'file' and item['name'] == 'pom.xml':
                    self.is_pom = True
                    self.config_file = self._fetch_file_content(item['url'])
                    if not os.path.exists(self.local_repo_dir):
                        subprocess.run(["git", "clone", self.url_path, self.local_repo_dir], check=True)
                    print(f"{self.name}'s pom.xml file fetched")
                elif item['type'] == 'file' and item['name'] == 'build.gradle':
                    # self.is_gradle = True
                    # self.config_file = self.fetch_file_content(item['url'])
                    raise Exception(f"Currently project doesn't admit Gradle projects")
        else:
            raise Exception(f"Failed to fetch repository contents. Status Code: {response.status_code}")

    def _fetch_file_content(self, file_url):
        response = requests.get(file_url, headers=self.headers)
        if response.status_code == 200:
            content = response.json().get('content', None)
            if content:
                return base64.b64decode(content).decode('utf-8')
        raise Exception(f"Failed to fetch file content. Status Code: {response.status_code}")

    def print_status(self):
        print(f"Repository: {self.name}")
        print(f"URL: {self.url_path}")
        print(f"Contains pom.xml: {'Yes' if self.is_pom else 'No'}")
        print(f"Contains build.gradle: {'Yes' if self.is_gradle else 'No'}")
        print(f"JSON generated: {self.json_generated}")