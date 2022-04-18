from requests import get as get_content, Response
from bs4 import BeautifulSoup
from engine.exceptions import PageNotAvailableError
from engine.utils import filter_text
from time import sleep


class Parser:
    def __init__(self, url: str, stop_words: iter, request_headers: dict, *exception_urls: str):
        self.main_url = url
        self.urls = []
        self.exception_urls = exception_urls
        self.headers = request_headers
        self.content_dict = {}
        self.stop_words = stop_words

    def get_urls(self):
        self.urls = []
        self._get_urls_from_page('')

    def _get_urls_from_page(self, page_url: str):
        file_formats = ('.pdf', '.txt', '.xlsx', '.ini', '.xls', '.doc', '.docx', '.ppt', '.pptx')
        content = self.status_code_handler(f'{self.main_url}/{page_url}')
        soup = BeautifulSoup(content.text, 'html.parser')
        self.content_dict[page_url] = filter_text(soup.get_text(), stop_words=self.stop_words)
        links_queue = []
        for tag in soup.find_all('a'):
            link = tag.get('href')
            if link is not None:
                if not (self.main_url not in link and '://' in link):
                    if self.main_url in link:
                        link = link.replace(self.main_url, '/')
                    if all(not link.startswith(exception)
                           for exception in self.exception_urls) and \
                            all(not link.lower().endswith(files_format)
                                for files_format in file_formats):
                        if link not in self.urls:
                            self.urls.append(link)
                            links_queue.append(link)
        print(len(self.content_dict))
        for link in links_queue:
            self._get_urls_from_page(link)

    def status_code_handler(self, url: str) -> Response:
        sleep(0.8)
        content = get_content(url, headers=self.headers)
        if content.status_code == 200:
            return content
        elif content.status_code == 404:
            return Response()
        else:
            raise PageNotAvailableError('Parsed page is not available')

    def get_info(self, url):
        content = get_content(url, headers=self.headers)
        soup = BeautifulSoup(content.text, 'html.parser')
        title = soup.find('title').get_text()
        tag = soup.find('meta', attrs={'name': 'description'})
        if tag is not None:
            text = tag.get('content') + ' ...'
        else:
            text = '...'
        return title, text
