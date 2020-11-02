#!/usr/bin/env python3

import argparse
import logging

from bs4 import BeautifulSoup
import requests

DEFAULT_ARCHIVES = 'https://slatestarcodex.com/archives/'
DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
}
DEFAULT_TEST_URLS = [
        'https://slatestarcodex.com/2014/07/30/meditations-on-moloch/',
        'https://slatestarcodex.com/2014/12/17/the-toxoplasma-of-rage/',
        'https://slatestarcodex.com/2015/04/21/universal-love-said-the-cactus-person/',
        'https://slatestarcodex.com/2020/',
]


def get_entry_content(url=None, headers=None, html_parser='html.parser'):
    """Get entry content of page."""
    # Defaults for testing.
    if url is None:
        url = DEFAULT_ARCHIVES
    if headers is None:
        headers = DEFAULT_HEADERS

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise requests.HTTPError("Got status code %d", resp.status_code)

    html = BeautifulSoup(resp.text, html_parser)

    div_tag = html.div
    entry_content = div_tag(attrs={'class': 'entry-content'})

    return entry_content


def get_links(url=None, headers=None, html_parser='html.parser'):
    """Scrape index/archives for links to blog posts to be scraped."""
    # Defaults for testing.
    if url is None:
        url = DEFAULT_ARCHIVES
    if headers is None:
        headers = DEFAULT_HEADERS

    entry_content = get_entry_content(
            url=url,
            headers=headers,
            html_parser=html_parser,
    )[0]

    html_links = entry_content.find_all('a')
    links = [html_link.get('href') for html_link in html_links]

    logging.info('Got %d links.', len(links))

    return links


def cull_links(
    links,
    patterns_to_remove=(
            'open-thread',
            'survey',
    ),
    remove_none=True,
    remove_only_year=True,
):
    num_input_links = len(links)
    logging.info('Got %d links input.', num_input_links)

    removed_links = []

    if remove_none is True:
        for i, link in enumerate(links):
            if link is None:
                del links[i]

    if remove_only_year is True:
        for i, link in enumerate(links):
            if len(link.split(sep='/')) == 4 or len(link.split(sep='/')) == 5:
                # Remove links of form
                #  https://slatestarcodex.com/2020/
                #  which splits to:
                #  ['https:', '', 'slatestarcodex.com', '2020', '']
                removed_links.append(link)
                del links[i]

    for i, link in enumerate(links):
        for pattern in patterns_to_remove:
            if pattern in link:
                removed_links.append(link)
                del links[i]

    logging.info(
            'Returning %d links; %d culled.',
            len(links),
            num_input_links - len(links),
    )
    logging.debug(
            'Culled links:\n%s',
            '\n'.join(removed_links),
    )

    return links


def scrape_page(url=None, headers=None, html_parser='html.parser'):
    """Scrape blog post. Specifically designed for SSC."""
    # Defaults for testing.
    if url is None:
        url = 'https://slatestarcodex.com/2014/12/17/the-toxoplasma-of-rage/'
    if headers is None:
        headers = DEFAULT_HEADERS

    entry_content = get_entry_content(
            url=url,
            headers=headers,
            html_parser=html_parser,
    )[0]

    return [paragraph for paragraph in entry_content.text.split('\n')]


def scrape_pages(urls=[], headers=None, html_parser='html.parser'):
    """Scrape blog posts. Specifically designed for SSC."""
    # Defaults for testing.
    if not urls:
        urls = DEFAULT_TEST_URLS
    if headers is None:
        headers = DEFAULT_HEADERS

    for url in urls:
        yield scrape_page(url=url, headers=headers, html_parser=html_parser)


def main():
    from format import format_paragraphs_to_docx
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='Comma-separated URL(s) to scrape.')
    parser.add_argument('--out', help='Location to output scraped page contents.')
    args = parser.parse_args()

    logging.basicConfig(
            format='[%(asctime)s] [%(funcName)s]: %(message)s',
            level=logging.INFO,
    )

    if args.url is not None:
        urls = args.url.split(sep=',')
    else:
        urls = DEFAULT_TEST_URLS

    logging.info('Got input URLs:\n%s', '\n'.join(urls))

    urls = cull_links(urls)
    logging.info('Post-culling URLs:\n%s', '\n'.join(urls))

    paras_generator = scrape_pages(urls)

    doc = None
    for paras in paras_generator:
        doc = format_paragraphs_to_docx(paras, doc=doc)

    if args.out is not None:
        doc.save(args.out)
    else:
        doc.save('scraped-site.docx')


if __name__ == '__main__':
    main()
