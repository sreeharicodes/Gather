import datetime
import base64
import requests
from bs4 import BeautifulSoup
from decouple import config


URL = "https://sdma.kerala.gov.in/dam-water-level/"


def get_soup(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.RequestException:
        return None


def get_pdf_urls(soup):
    urls = []
    div = soup.find("div", class_="entry-content")
    li_tags = div.find_all("li")
    for li in li_tags:
        name = li.text.strip()
        a_tag = li.find('a', href=True)
        href = a_tag.attrs.get("href")
        urls.append({
            "name": name,
            "url": href
        })

    return urls

class GitHubAPI:
    def __init__(self):
        self.base_url = "https://api.github.com/repos"
        self.repo = "Gather"
        self.owner = "sreehari1997"
        self.token = config("ACCESS_TOKEN")
        self.branch = "main"

    def get_headers(self):
        headers = {
            'Authorization': 'Bearer {}'.format(self.token),
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 6.1; Win64; '
                'x64; rv:47.0) Gecko/20100101 Firefox/47.0'
            ),
            'X-GitHub-Api-Version': '2022-11-28',
            'Accept': 'application/vnd.github+json'
        }
        return headers

    def get(self, url):
        try:
            response = requests.get(
                url,
                headers=self.get_headers()
            )
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def post(self, url, data):
        try:
            response = requests.post(
                url,
                headers=self.get_headers(),
                data=data
            )
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def patch(self, url, data):
        try:
            response = requests.patch(
                url,
                headers=self.get_headers(),
                data=data
            )
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def put(self, url, data):
        try:
            response = requests.put(
                url,
                headers=self.get_headers(),
                json=data
            )
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def get_blob(self, url):
        try:
            response = requests.get(url)
            return response.content
        except requests.exceptions.RequestException:
            return None

    def get_last_commit_sha(self):
        # https://api.github.com/repos/sreehari1997/Gather/branches/main
        url = "{}/{}/{}/branches/{}".format(
            self.base_url,
            self.owner,
            self.repo,
            self.branch
        )
        data = self.get(url)
        if data:
            return data["commit"]["sha"]
        else:
            return None

    def get_last_commit_message(self):
        # https://api.github.com/repos/sreehari1997/Gather/branches/main
        url = "{}/{}/{}/branches/{}".format(
            self.base_url,
            self.owner,
            self.repo,
            self.branch
        )
        data = self.get(url)
        if data:
            return data["commit"]["commit"]["message"]
        else:
            return None

    def create_file(self, content, path, commit_message):
        # This worked
        encoded = str(base64.b64encode(content).decode("utf-8"))
        data = {
            "message": commit_message,
            "committer": {
                "name": "sreehari1997",
                "email": "sreehaivijayan619@gmail.com"
            },
            "content": encoded
        }
        url = "{}/{}/{}/contents/{}".format(
            self.base_url,
            self.owner,
            self.repo,
            path
        )
        response = self.put(url, data)
        return response

    def create_blob(self, content):
        encoded = str(base64.b64encode(content).decode("utf-8"))
        data = {
            "content": encoded,
            "encoding": "base64"
        }
        url = "{}/{}/{}/git/blobs".format(
            self.base_url,
            self.owner,
            self.repo
        )
        response = self.post(url, data)
        if response:
            print(response)
            return response["sha"]
        else:
            return None

    def create_tree(self, commit_sha, blob_sha):
        data = {
          "base_tree": commit_sha,
          "tree": [
            {
              "path": "2023/December/Water Levels of Main Reservoirs (KSEB) - 03/12/2023.pdf",
              "mode": "100644",
              "type": "blob",
              "sha": blob_sha
            }
          ]
        }
        url = "{}/{}/{}/git/trees/".format(
            self.base_url,
            self.owner,
            self.repo
        )
        response = self.post(url, data)
        if response:
            return response["sha"]
        else:
            return None

    def create_commit(self, commit_sha, tree_sha):
        data = {
          "message": "Add new files at once programatically",
          "author": {
            "name": "sreehari1997",
            "email": "sreeharivijayan619@gmail.com"
          },
          "parents": [
            commit_sha
          ],
          "tree": tree_sha
        }
        url = "{}/{}/{}/git/commits/".format(
            self.base_url,
            self.owner,
            self.repo
        )
        response = self.post(url, data)
        if response:
            return response["sha"]
        else:
            return None


    def update_reference(self, commit_sha):
        data = {
            "sha": commit_sha
        }
        url = "{}/{}/{}/git/refs/heads/{}".format(
            self.base_url,
            self.owner,
            self.repo,
            self.branch
        )
        response = self.post(url, data)
        if response:
            return response
        else:
            return None


def is_todays_data(filename, now):
    try:
        date_str = filename.split('–')[1].strip()
        date_str = date_str.split(".")[0]
        today = now.strftime("%d/%m/%Y")
        if today == date_str:
            return True
    except Exception as e:
        print(e)

    return False


def driver():
    github_client = GitHubAPI()
    now = datetime.datetime.now()
    last_commit_message = github_client.get_last_commit_message()
    time_str = now.strftime("%d-%m-%Y")
    if last_commit_message != time_str:
        print("Pushing....")
        soup = get_soup(URL)
        urls = get_pdf_urls(soup)
        directory = "{}/{}/{}/".format(
            now.year,
            now.month,
            now.day
        )
        for url in urls:
            if is_todays_data(url["name"], now):
                content = github_client.get_blob(
                    url["url"]
                )
                filename = url["name"].split(".")[0]
                path = "{}{}.pdf".format(
                    directory,
                    filename.replace("/", "-")
                )
                data = github_client.create_file(
                    content,
                    path,
                    time_str
                )
                print(data)
    else:
        print("not pushing..")

if __name__ == "__main__":
    driver()
