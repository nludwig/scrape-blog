#!/usr/bin/env python3

import argparse
import logging

from bs4 import BeautifulSoup
import requests

import format as f
import scrape

NUM_TEST_URLS = 10


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '--out',
            help='Location to output scraped page contents.',
    )
    parser.add_argument(
            '--test',
            help='Test? -> only grab first {NUM_TEST_URLS} URLs.',
            type=bool,
            default=True,
    )
    args = parser.parse_args()

    if args.test is True:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(
            format='[%(asctime)s] [%(funcName)s]: %(message)s',
            level=log_level,
    )

    blog_post_urls = scrape.get_links()

    culled_urls = scrape.cull_links(blog_post_urls)

    # Put into time-increasing order.
    culled_urls.reverse()

    if args.test:
        logging.info(
                'Test run. Grabbing only first %d URLs',
                NUM_TEST_URLS,
        )
        culled_urls = culled_urls[:NUM_TEST_URLS]

    pages_generator = scrape.scrape_pages(culled_urls)

    doc = None
    for title, paras in pages_generator:
        doc = f.format_paragraphs_to_docx(title, paras, doc=doc)

    if args.out is not None:
        doc.save(args.out)
    else:
        doc.save('site.docx')


if __name__ == '__main__':
    main()
