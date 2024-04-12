import logging
import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


PR_COLLAPSIBLE_TEMPLATE = """
<details>
<summary>{comment}</summary>

##### Reason
{reasoning}

##### Confidence
{confidence}
</details>
"""

DESC_COLLAPSIBLE_TEMPLATE = """
<details>
<summary>Original Description</summary>
{desc}
</details>
"""


def merge_topics(reviews):
    topics = {}
    for review in reviews:
        if review["topic"] in topics:
            topics[review["topic"]].append(review)
        else:
            topics[review["topic"]] = [review]
    return topics


def create_pr_review_from_json(data):
    markdown_output = "## Code Review Feedback\n\n"

    topics = merge_topics(data["review"])

    for topic, reviews in topics.items():
        markdown_output += f"### {topic}\n\n"
        for review in reviews:
            ct = PR_COLLAPSIBLE_TEMPLATE.format(
                comment=review.get("comment", "NA"),
                reasoning=review.get("reasoning", "NA"),
                confidence=review.get("confidence", "NA"),
            )
            markdown_output += ct + "\n"

    return markdown_output


def create_pr_description(data, original_desc):
    markdown_output = "## Autogenerated PR Description \n\n"
    markdown_output += data["desc"]
    markdown_output += "\n\n -- Generated with love by Cloud Code AI"
    markdown_output += "\n\n" + DESC_COLLAPSIBLE_TEMPLATE.format(desc=original_desc)
    return markdown_output


async def get_html(url):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url, {'waitUntil': 'networkidle2'})
    html = await page.content()
    await browser.close()
    return html


def get_web_html(url):
    html = asyncio.get_event_loop().run_until_complete(get_html(url))
    soup = BeautifulSoup(html, 'html.parser')
    pretty_html = soup.prettify()
    return pretty_html
