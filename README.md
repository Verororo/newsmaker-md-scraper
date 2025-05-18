# newsmaker-md-scraper

A simple scraper for the Russian version of the news website [NewsMaker](https://newsmaker.md/ru). The articles are scrapped from the "News" ("Новости") category.

## Usage

Write
`python scraper.py [num_pages?]`
in the console.

`num_pages` is the amount of pages to scrap, including the landing page. Default is `30`. Each page contains 10 articles.

Scrapped articles would then be written to `output.json`.

## Details

New pages are accessed dynamically via POST requests. This scraper simulates them by providing the same headers and payload that are used when accessing the pages from a web browser. Some of the fields in them used here may be unnecessary.

To speed up the scraping, each request is done asynchronically.