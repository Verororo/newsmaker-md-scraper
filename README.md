# newsmaker-md-scraper

A simple scraper for the Russian version of the news website [NewsMaker](https://newsmaker.md/ru). The articles are scrapped from the "News" ("Новости") category.

## Usage

Write
`python scraper.py [num_pages?]`
in the console.

`num_pages` is the amount of pages to scrap, including the landing page. Its default value is `30`.

Scrapped articles are written to `output.json`.

## Details

NewsMaker implements pagination dynamically via POST requests. This scraper simulates them by providing the same headers and payload that are used when accessing the pages with a web browser. Some of the headers/payload fields used in the script may be unnecessary for the simulation.

To speed up the scraping, each request is done asynchronously.

## Dependencies

This script depends on the external library `aiohttp` to execute HTTP requests asynchronously. You can install it via `pip`.
