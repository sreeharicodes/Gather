from datetime import datetime
from utils import (
    WebScraper,
    RiverScraper,
    DamScraper,
    GitHubAPI
)

DAM_URL = "https://sdma.kerala.gov.in/dam-water-level/"
RIVER_URL = "https://sdma.kerala.gov.in/flood-homescreen/"

"""
Dam
Water Levels of Main Reservoirs (KSEB) – 09/12/2023.PDF
Irrigation Dams/Reservoir Status (Irrigation) – 09/12/2023. PDF
River
1.River Water Level – MAP (CWC)
2. River Water Level – TABLE (CWC)
പുറപ്പെടുവിച്ച സമയം 12.00 PM 09.12.2023
"""

def driver():
    dams = DamScraper(DAM_URL)
    rivers = RiverScraper(RIVER_URL)
    sources = dams.get_source_urls()
    sources.extend(rivers.get_source_urls())
    if sources:
        github_client = GitHubAPI()
        now = datetime.now()
        time_str = now.strftime("%d-%m-%Y")
        last_commit_msg = github_client.get_last_commit_message()
        if last_commit_msg and last_commit_msg == now.strftime("%d-%m-%Y"):
            directory = "{}/{}/{}/".format(
                now.year,
                now.month,
                now.day
            )
            for source in sources:
                scraper = WebScraper(source["url"])
                content = scraper.get_blob()
                path = "{}{}.{}".format(
                    directory,
                    source["name"],
                    source["type"]
                )
                _ = github_client.create_file(
                    content,
                    path,
                    time_str
                )

if __name__ == "__main__":
    driver()