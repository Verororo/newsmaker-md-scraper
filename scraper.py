import time
import json
import aiohttp
import asyncio
import argparse
from bs4 import BeautifulSoup
from urllib.parse import parse_qs

base_url = "https://newsmaker.md/ru/category/news"
next_page_url = "https://newsmaker.md/ru/category/news?jsf_ajax=1"

headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
#    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'ru,ru-RU;q=0.9,en;q=0.8,en-US;q=0.7',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'dnt': '1',
    'origin': 'https://newsmaker.md',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://newsmaker.md/ru/category/news',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}

base_payload_str = "action=jet_smart_filters&provider=epro-loop-builder%2Fdefault&defaults%5Bpost_status%5D%5B%5D=publish&defaults%5Bpost_status%5D%5B%5D=private&defaults%5Bcategory_name%5D=news&defaults%5Berror%5D=&defaults%5Bm%5D=&defaults%5Bp%5D=0&defaults%5Bpost_parent%5D=&defaults%5Bsubpost%5D=&defaults%5Bsubpost_id%5D=&defaults%5Battachment%5D=&defaults%5Battachment_id%5D=0&defaults%5Bname%5D=&defaults%5Bpagename%5D=&defaults%5Bpage_id%5D=0&defaults%5Bsecond%5D=&defaults%5Bminute%5D=&defaults%5Bhour%5D=&defaults%5Bday%5D=0&defaults%5Bmonthnum%5D=0&defaults%5Byear%5D=0&defaults%5Bw%5D=0&defaults%5Btag%5D=&defaults%5Bcat%5D=1&defaults%5Btag_id%5D=&defaults%5Bauthor%5D=&defaults%5Bauthor_name%5D=&defaults%5Bfeed%5D=&defaults%5Btb%5D=&defaults%5Bmeta_key%5D=&defaults%5Bmeta_value%5D=&defaults%5Bpreview%5D=&defaults%5Bs%5D=&defaults%5Bsentence%5D=&defaults%5Btitle%5D=&defaults%5Bfields%5D=&defaults%5Bmenu_order%5D=&defaults%5Bembed%5D=&defaults%5Bsuppress_filters%5D=false&defaults%5Bcache_results%5D=true&defaults%5Bupdate_post_term_cache%5D=true&defaults%5Bupdate_menu_item_cache%5D=false&defaults%5Blazy_load_term_meta%5D=true&defaults%5Bupdate_post_meta_cache%5D=true&defaults%5Bpost_type%5D=&defaults%5Bnopaging%5D=false&defaults%5Bcomments_per_page%5D=50&defaults%5Bno_found_rows%5D=false&defaults%5Border%5D=DESC&settings%5Bwidget_id%5D=163aff9&settings%5Bfiltered_post_id%5D=866422&settings%5Bjsf_signature%5D=ab9bd4fd43febd54e9ec0c5304c976bf&props%5Bfound_posts%5D=6880&props%5Bmax_num_pages%5D=688&props%5Bpage%5D=4&props%5Bpages%5D%5B%5D=1&props%5Bpages%5D%5B%5D=2&props%5Bpages%5D%5B%5D=3&props%5Bpages%5D%5B%5D=4&props%5Bpages%5D%5B%5D=5&paged=5&indexing_filters=%5B871139%5D"
base_payload_dict = parse_qs(base_payload_str)

async def get_next_page_content(page_k, session):
    """
    Asynchronously fetches and processes a single subsequent page.
    page_k is the 1-based index of the previously loaded page (e.g., if page 1 is loaded, page_k=1 to fetch page 2).
    Returns HTML content as a string, or None if an error occurs.
    """
    page_to_fetch = page_k + 1
    current_max_page_in_ui = page_k
    
    current_payload = {key: list(value) for key, value in base_payload_dict.items()}
    current_payload['paged'] = [str(page_to_fetch)]
    current_payload['props[page]'] = [str(current_max_page_in_ui)]

    pages_list_for_props = [str(p) for p in range(1, page_to_fetch + 1)]
    current_payload['props[pages][]'] = pages_list_for_props


    print(f"Requesting page {page_to_fetch} (props[page] set to {current_max_page_in_ui})")
    try:
        async with session.post(next_page_url, headers=headers, data=current_payload, timeout=20) as response:
            response.raise_for_status()
        
            response_json = await response.json(content_type=None)
        
            html_content = None
            possible_html_keys = ['content', 'html', 'template', 'data']
        
            for key in possible_html_keys:
                if key in response_json:
                    if key == 'data' and isinstance(response_json[key], dict):
                        for sub_key in ['html', 'content']:
                            if sub_key in response_json[key]:
                                html_content = response_json[key][sub_key]
                                break
                    elif isinstance(response_json[key], str):
                         html_content = response_json[key]
                    
                    if html_content:
                        break
            
            if html_content:
                print(f"Successfully fetched and extracted HTML for page {page_to_fetch} (length: {len(html_content)} chars).")
                return html_content
            else:
                print(f"Warning: Could not find HTML content in JSON response for page {page_to_fetch}.")
                print(f"Available JSON keys: {list(response_json.keys())}")
                print(f"Response snippet: {str(response_json)[:200]}...")
                return None

    except asyncio.TimeoutError:
        print(f"  Error: Timeout while fetching page {page_to_fetch}.")
        return None
    except aiohttp.ClientResponseError as http_err:
        response_text = await response.text()
        print(f"Error: HTTP error while fetching page {page_to_fetch}: {http_err.status} {http_err.message}")
        print(f"Response content snippet: {response_text[:200]}")
        return None
    except aiohttp.ClientError as client_err:
        print(f"Error: Client error while fetching page {page_to_fetch}: {client_err}")
        return None
    except json.JSONDecodeError:
        try:
            error_response_text = await response.text()
            print(f"Error: Failed to decode JSON response for page {page_to_fetch}.")
            print(f"Response text snippet: {error_response_text[:200]}...")
        except Exception as e_text:
            print(f"Error: Failed to decode JSON and also failed to get text response for page {page_to_fetch}: {e_text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching page {page_to_fetch}: {e}")
        return None


async def main(num_pages_to_parse):
    """
    Main asynchronous function to coordinate all fetches and parsing.
    num_pages_to_parse_arg: Total number of pages to parse, including the first one.
    """
    full_html_parts = []
    
    async with aiohttp.ClientSession() as session:
        # Get the landing page HTML
        print(f"Fetching initial page: {base_url}")
        try:
            async with session.get(base_url, headers={k:v for k,v in headers.items() if k != 'content-type'}, timeout=20) as response:
                response.raise_for_status()
                initial_html = await response.text()
                full_html_parts.append(initial_html)
                print(f"Successfully fetched initial page (length: {len(initial_html)} chars).")

        except Exception as e:
            print(f"An unexpected error occurred during initial page fetch: {e}")
            return

        # Get the HTML from other pages
        tasks = []
        for page_k in range(1, num_pages_to_parse):
            tasks.append(asyncio.create_task(get_next_page_content(page_k, session)))
        results = await asyncio.gather(*tasks)

    # Append the HTML from other pages
    for page in results:
        if page:
            full_html_parts.append(page)

    if not full_html_parts:
        print("No HTML content was fetched. Exiting.")
        return

    full_html_text = "".join(full_html_parts)
    
    # Extracting articles info from the HTML
    print("\nParsing combined HTML content...")
    soup = BeautifulSoup(full_html_text, 'html.parser')
    articles = soup.find_all(class_='e-loop-item')
    parsed_article_list = list()
    
    for article_id, article in enumerate(articles):
        parsed_article = dict()
    
        # Type of the article (Новости, Партнерство, Жизнь, etc)
        type_wrapped = article.find(class_='elementor-icon-list-text')
        if type_wrapped and type_wrapped.a and type_wrapped.a.string:
            parsed_article['type'] = type_wrapped.a.string.strip()
    
        # Title
        title_wrapped = article.find(class_='elementor-heading-title')
        if title_wrapped and title_wrapped.a and title_wrapped.a.string:
            title = title_wrapped.a.string.strip().replace('\xa0', ' ')
            parsed_article['title'] = title
    
        # Description
        description_wrapped = article.find(class_='elementor-widget-theme-post-excerpt')
        if description_wrapped and description_wrapped.div and description_wrapped.div.p and description_wrapped.div.p.string:
            description = description_wrapped.div.p.string.strip()
            description = description.replace('\xa0', ' ').replace('\t', '')
            parsed_article['description'] = description
    
        # Author(s)
        authors_wrapped = article.find(class_='elementor-post-info__terms-list')
        if authors_wrapped:
            authors = []
            for author in authors_wrapped:
                if author.string:
                    name = author.string.replace('\\n', ' ').strip()
                    if name != "" and name != ",":
                        authors.append(name)

            parsed_article['authors'] = authors
    
        # Post date
        date_tag = article.find(class_='elementor-post-info__item--type-date')
        if date_tag and date_tag.time and date_tag.time.string:
            parsed_article['date'] = date_tag.time.string.strip()
    
        # Post time
        time_tag = article.find(class_='elementor-post-info__item--type-time')
        if time_tag and time_tag.time and time_tag.time.string:
            parsed_article['time'] = time_tag.time.string.strip()
    
        if parsed_article.get('title'):
            parsed_article_list.append(parsed_article)
        else:
            print(f"Skipping article index {article_id} due to missing title (potential non-article element).")
    
    print(f"Successfully parsed {len(parsed_article_list)} articles.")

    output_filename = 'output.json'
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(parsed_article_list, f, ensure_ascii=False, indent=2)
            print(f"Results saved in {output_filename}.")
    except Exception as e:
        print(f"An unexpected error occurred while saving JSON to {output_filename}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape articles from newsmaker.md.")
    parser.add_argument(
        "num_pages",
        type=int,
        nargs='?',
        default=30,
        help="Total number of pages to parse (including the first page). Default is 30."
    )
    args = parser.parse_args()

    asyncio.run(main(args.num_pages))

