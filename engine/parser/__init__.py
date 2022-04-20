from requests import get as get_content, Response
from bs4 import BeautifulSoup
from engine.exceptions import PageNotAvailableError
from engine.utils import filter_text
from time import sleep


class Parser:
    def __init__(self, url: str, stop_words: iter,
                 request_headers: dict, exception_urls: list,
                 additional_urls: list):
        self.main_url = url
        self.urls = additional_urls
        self.exception_urls = exception_urls
        self.headers = request_headers
        self.content_dict = {}
        self.stop_words = stop_words

    def change_url(self, url: str):
        self.main_url = url

    def get_urls(self):
        self.urls = []
        self._get_urls_from_page(self.main_url)

    def filter_link(self, link_url: str) -> bool:
        file_formats = ('.pdf', '.txt', '.xlsx', '.ini', '.xls',
                        '.doc', '.docx', '.ppt', '.pptx', '.json')
        spec_symbols = ('?', '#', '@')
        if all(exception not in link_url
               for exception in self.exception_urls) and \
                all(not link_url.lower().endswith(files_format)
                    for files_format in file_formats) and \
                all(spec_symbol not in link_url
                    for spec_symbol in spec_symbols):
            return True
        return False

    def _get_urls_from_page(self, page_url: str):
        content = self.status_code_handler(page_url)
        soup = BeautifulSoup(content.text, 'html.parser')

        self.content_dict[page_url] = \
            filter_text(soup.get_text(),
                        stop_words=self.stop_words)

        links_queue = []
        for tag in soup.find_all('a'):
            link = tag.get('href')
            if link is not None:
                root_url = page_url.split('//')[1].split('/')[0]
                main_protocol = self.main_url.split('//')[0] + '//'
                if link.startswith('//'):
                    link = link.replace('//', main_protocol)
                else:
                    if '://' not in link:
                        if not link.startswith('/'):
                            link = '/' + link
                        link = main_protocol + root_url + link
                    elif root_url in link:
                        pass
                    else:
                        continue
                if self.filter_link(link):
                    if link not in self.urls:
                        self.urls.append(link)
                        links_queue.append(link)
        for link in links_queue:
            self._get_urls_from_page(link)

    def status_code_handler(self, url: str) -> Response:
        sleep(1)
        content = get_content(url, headers=self.headers)
        if content.status_code == 200:
            return content
        elif content.status_code == 404:
            return Response()
        else:
            raise PageNotAvailableError('Parsed page is not available. HTTP code: ' + str(content.status_code))

    def get_info(self, url: str) -> (str, str):
        content = self.status_code_handler(url)
        soup = BeautifulSoup(content.text, 'html.parser')
        title = soup.find('title').get_text()
        tag = soup.find('meta', attrs={'name': 'description'})
        if tag is not None:
            text = tag.get('content') + ' ...'
        else:
            words = soup.get_text('').strip().split()
            try:
                text = ' '.join(words[:25])
            except IndexError:
                text = ' '.join(words)
        return title, text
