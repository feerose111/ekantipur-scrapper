import json

from playwright.sync_api import Page , sync_playwright


def get_entertainment_news(page: Page) -> list[dict]:
    """Scrapes top 5 entertainment news from the ekantipur entertainment page"""
    print("Starting entertainment news scraping")

    # Navigate to the entertainment news page
    page.goto("https://ekantipur.com/entertainment")
    page.wait_for_selector(".category-inner-wrapper")
    page.wait_for_load_state("networkidle")

    # Get the first 5 articles
    articles = page.query_selector_all(".category-inner-wrapper")[:5]
    print(f"Found {len(articles)} articles")

    news_data = []

    category_element = page.query_selector(".category-name p a")
    category = category_element.text_content().strip() if category_element else "मनोरञ्जन"

    # Scrape the data from the articles
    for article in articles:
        try:
            title_element = article.query_selector("h2 a")
            title = title_element.text_content().strip() if title_element else None

            image_element = article.query_selector(".category-image img")
            #articles 3-5 are lazy loaded so they use data-src instead of src.
            #Just check both: if not checked both it will only return null except first two
            if image_element:
                image_url = image_element.get_attribute("src") or image_element.get_attribute("data-src")
            else:
                image_url = None

            author_element = article.query_selector(".author-name p a")
            author = author_element.text_content().strip() if author_element else None


            news_data.append({
                "title": title,
                "image_url": image_url,
                "category" : category,
                "author": author,
            })
            print(f"Scraped: {title}") #verifying in terminal as we go, print title of the article

        except Exception as e:
            print(f"Error scraping article: {e}")

    return news_data


def get_cartoon(page: Page) -> dict:
    """scrapes the most recent cartoon for cartoon of the day"""

    print("starting scrapping cartoon of the day")

    page.goto("https://ekantipur.com/cartoon")
    page.wait_for_selector(".cartoon-wrapper") 
    page.wait_for_load_state("networkidle")

    cartoons = page.query_selector_all(".cartoon-wrapper")

    if not cartoons:
        print("Cartoon not found")
        return {}

    try:
        # take the first (most recent) cartoon
        first_cartoon = cartoons[0]

        image_element = first_cartoon.query_selector(".cartoon-image img")
        image_url = image_element.get_attribute("src") if image_element else None

        title = image_element.get_attribute("alt").strip() if image_element else None

        # The title and author were in the same element cartoon-description separated by "-",
        # so we need to split the text and get the title and author

        desc_element = first_cartoon.query_selector(".cartoon-description p")
        desc_text = desc_element.text_content().strip() if desc_element else ""

        # normalize both separators to a single split
        for separator in [" - ", " : "]:
            if separator in desc_text:
                author = desc_text.split(separator)[-1].strip() or None
                break
        else:
            author = None

        print(f"Cartoon: {title} by {author}")


        cartoon_data = {
            "title": title,
            "image_url": image_url,
            "author": author,
        }


        return cartoon_data

    except Exception as e:
        print(f"Error scraping cartoon: {e}")
        return {}


def save_output(data):
    """Save the output to a JSON file"""
    try:
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Output saved to output.json successfully")

    except Exception as e:
        print(f"Error saving output: {e}")

def main():
    """Main funtion to run the entire code"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            entertainment_news = get_entertainment_news(page)
            cartoon_data = get_cartoon(page)

            save_output({
                "entertainment_news": entertainment_news,
                "cartoon_of_the_day": cartoon_data
            })
            print(f"Scraped {len(entertainment_news)} entertainment news articles")
            print(f"Scrapped cartoon title - {cartoon_data["title"]}")

            browser.close()

    except Exception as e:
        print(f"MAIN ERROR: {e}")


if __name__ == "__main__":
    main() 
