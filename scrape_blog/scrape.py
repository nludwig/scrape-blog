#!/usr/bin/env python3

import argparse
import logging
import shutil
import tempfile

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


def get_entry(url=None, headers=None, html_parser='html.parser'):
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
    entry_title = div_tag(attrs={'class': 'entry-header'})[0].h1.string
    entry_content = div_tag(attrs={'class': 'entry-content'})

    return entry_title, entry_content


def get_links(url=None, headers=None, html_parser='html.parser'):
    """Scrape index/archives for links to blog posts to be scraped."""
    # Defaults for testing.
    if url is None:
        url = DEFAULT_ARCHIVES
    if headers is None:
        headers = DEFAULT_HEADERS

    _, entry_content = get_entry(
            url=url,
            headers=headers,
            html_parser=html_parser,
    )
    entry_content = entry_content[0]

    html_links = entry_content.find_all('a')
    links = [html_link.get('href') for html_link in html_links]

    logging.info('Got %d links.', len(links))

    return links


def cull_links(
    links,
    patterns_to_remove=(
            'open-thread',
            'survey',
            'links-',
            '/ot',
    ),
    remove_none=True,
    remove_only_year=True,
    required_patterns=tuple(),
):
    num_input_links = len(links)
    logging.info('Got %d links input.', num_input_links)

    removed_links = []

    if remove_none is True:
        i = 0
        while i < len(links):
            if links[i] is None:
                del links[i]
            else:
                i += 1

    if remove_only_year is True:
        i = 0
        while i < len(links):
            if len(links[i].split(sep='/')) == 4 \
                    or len(links[i].split(sep='/')) == 5:
                # Remove links of form
                #  https://slatestarcodex.com/2020/
                #  which splits to:
                #  ['https:', '', 'slatestarcodex.com', '2020', '']
                removed_links.append(links[i])
                del links[i]
            else:
                i += 1

    for pattern in patterns_to_remove:
        i = 0
        while i < len(links):
            if pattern in links[i]:
                removed_links.append(links[i])
                del links[i]
            else:
                i += 1

    if required_patterns:
        for pattern in required_patterns:
            i = 0
            while i < len(links):
                if pattern not in links[i]:
                    removed_links.append(links[i])
                    del links[i]
                else:
                    i += 1

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

    entry_title, entry_content = get_entry(
            url=url,
            headers=headers,
            html_parser=html_parser,
    )
    entry_content = entry_content[0]

    paragraphs = entry_content.find_all('p')

    return entry_title, paragraphs


def scrape_pages(urls=[], headers=None, html_parser='html.parser'):
    """Scrape blog posts. Specifically designed for SSC."""
    # Defaults for testing.
    if not urls:
        urls = DEFAULT_TEST_URLS
    if headers is None:
        headers = DEFAULT_HEADERS

    for url in urls:
        yield scrape_page(url=url, headers=headers, html_parser=html_parser)


def textify_text_imgify_imgs(
        paragraphs,
        headers=None,
        image_patterns_to_remove=None
):
    """
    Assume all paragraphs may contain images and/or text and yield these
    (images yielded first).
    """

    # Defaults for testing.
    if image_patterns_to_remove is None:
        image_patterns_to_remove = (
                'amazon-adsystem',
        )
    if headers is None:
        headers = DEFAULT_HEADERS

    for paragraph in paragraphs:
        img_html = paragraph.find('img')
        if img_html is not None:
            src_url = img_html['src']
            for pattern in image_patterns_to_remove:
                if pattern in src_url:
                    logging.info(
                            'Excluding img url %s: got pattern %s',
                            src_url,
                            pattern,
                    )
                    src_url = None
                    break

            if src_url is not None:
                try:
                    response = requests.get(
                            src_url,
                            headers=headers,
                            stream=True,
                    )
                except Exception:
                    logging.error(
                            "Exception getting image from URL %s:",
                            src_url,
                            exc_info=True,
                    )
                    yield None
                else:
                    if response.status_code == 200:
                        f = tempfile.TemporaryFile()
                        response.raw.decode_content = True
                        shutil.copyfileobj(response.raw, f)
                        yield {'img': f, 'width': img_html.get('width')}
                    else:
                        logging.error(
                                'Could not get image from %s; code %d',
                                src_url,
                                response.status_code,
                        )
                        yield None
            else:
                yield None

        if paragraph.text != '':
            yield paragraph.text


def main():
    from format import format_paragraphs_to_docx
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='Comma-separated URL(s) to scrape.')
    parser.add_argument('--out', help='Location to output scraped page contents.')
    args = parser.parse_args()

    logging.basicConfig(
            format='[%(asctime)s] [%(levelname)s] [%(funcName)s]:'
                   ' %(message)s',
            level=logging.INFO,
    )

    if args.url is not None:
        urls = args.url.split(sep=',')
    else:
        urls = DEFAULT_TEST_URLS

    logging.info('Got input URLs:\n%s', '\n'.join(urls))

    urls = cull_links(urls)
    logging.info('Post-culling URLs:\n%s', '\n'.join(urls))

    pages_generator = scrape_pages(urls)

    doc = None
    for title, paras in pages_generator:
        paras = textify_text_imgify_imgs(paras)
        doc = format_paragraphs_to_docx(title, paras, doc=doc)

    if args.out is not None:
        doc.save(args.out)
    else:
        doc.save('site.docx')


if __name__ == '__main__':
    main()
