from loguru import logger
import click
from urllib.parse import urljoin
import requests
from normalise import normalise
import csv
from os.path import join

BASE_URL = "https://api.stackexchange.com/2.2"
END_POINT = "/questions"
DATA_DIR = "data"


@click.command()
@click.option("--pages", default=1)
def crawl(pages: int = 1):
    url = urljoin(BASE_URL, END_POINT)
    total_rows = []
    total_formatted_rows = []

    for i in range(1, pages + 1):
        try:
            parameters = {
                "order": "desc",
                # "sort": "activity",
                "site": "stackoverflow",
                "filter": "withbody",
                "page": i,
                "pagesize": 100,
            }
            response = requests.get(url, params=parameters)
            if response.status_code >= 400:
                e = Exception(
                    f"HTTP Error calling {url} => {response.status_code} : {response.text}"
                )
                logger.error(e)
                raise e
            response_json = response.json()
            if not response_json.get("has_more", False):
                logger.error("Quota exceeded")
                break
            else:
                logger.info(
                    f"Quota remaining : {response_json.get('quota_remaining', -1)}"
                )
            formatted_rows, rows = parse(response_json)
            total_rows += rows
            total_formatted_rows += formatted_rows
        except Exception as e:
            logger.error(e)
            raise e

    write_rows(total_formatted_rows, join(DATA_DIR, "corpus.txt"), join(DATA_DIR, "corpus_test.txt"), 0.1)
    write_csv(total_rows, join(DATA_DIR, "corpus.csv"))


def parse(response):
    rows = []
    formatted_rows = []
    for item in response.get("items", []):
        first_tag = item.get("tags", ["na"])[0]
        title = normalise(item.get("title", ""))
        body = normalise(item.get("body", ""))

        formatted_rows.append(f"{title} {body} __label__{first_tag} \n")
        rows.append([title, body, first_tag, "|".join(item.get("tags", ["na"]))])

    return formatted_rows, rows


def write_csv(rows, output_file):
    with open(output_file, "w", encoding="utf-8") as csvfile:
        datawriter = csv.writer(csvfile, delimiter=";")
        datawriter.writerows(rows)


def write_rows(rows, output_file, output_file_test, percentage_test=0.0):
    cut_off = int(len(rows) * percentage_test)

    logger.debug(f"Limit for test data is {cut_off}")
    with open(output_file_test, "w", encoding="utf-8") as test_txt_file:
        for current_row in rows[:cut_off]:
            test_txt_file.write(current_row)

    with open(output_file, "w", encoding="utf-8") as txt_file:
        for current_row in rows[cut_off:]:
            txt_file.write(current_row)


if __name__ == "__main__":
    crawl()
