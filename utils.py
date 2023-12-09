import requests
from bs4 import BeautifulSoup
from datetime import datetime
from decouple import config
import base64


class WebScraper:

    def __init__(self, url):
        self.url = url

    def get_soup(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException:
            return None

    def get_blob(self):
        try:
            response = requests.get(self.url)
            return response.content
        except requests.exceptions.RequestException:
            return None

    @staticmethod
    def clean_name(name):
        return name.strip().replace("/", "-").replace(".", "-")


class DamScraper(WebScraper):
    data = []

    @staticmethod
    def is_todays_data(filename):
        try:
            date_str = filename.split('–')[1].strip()
            date_str = date_str.split(".")[0]
            today = datetime.now().strftime("%d/%m/%Y")
            if today == date_str:
                return True
        except Exception:
            pass

        return False

    def get_source_urls(self, filetype="pdf"):
        soup = self.get_soup()
        if soup:
            div = soup.find("div", class_="entry-content")
            li_tags = div.find_all("li")
            for li in li_tags:
                name = li.text.strip()
                if self.is_todays_data(name):
                    a_tag = li.find('a', href=True)
                    href = a_tag.attrs.get("href")
                    self.data.append({
                        "name": self.clean_name(name),
                        "url": href,
                        "type": filetype
                    })

        return self.data


class RiverScraper(WebScraper):
    data = []

    @staticmethod
    def is_todays_data(date_str):
        try:
            date_str = date_str.split('M')[1].strip()
            today = datetime.now().strftime("%d.%m.%Y")
            if today == date_str:
                return True
        except Exception:
            pass

        return False

    def get_source_urls(self, filetype="jpeg"):
        soup = self.get_soup()
        if soup:
            div = soup.find("div", class_="entry-content")
            p_tags = div.find_all("p")
            try:
                p_tags = p_tags[1:4]
            except IndexError:
                return self.data

            date_str = p_tags.pop(-1)
            if self.is_todays_data(date_str.text):
                for p in p_tags:
                    name = p.text.strip()
                    a_tag = p.find('a', href=True)
                    href = a_tag.attrs.get("href")
                    self.data.append({
                        "name": self.clean_name(name),
                        "url": href,
                        "type": filetype
                    })

        return self.data


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

    def get_last_commit_message(self):
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
