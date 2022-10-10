import os
import requests
import string
from bs4 import BeautifulSoup

url_nature = "https://www.nature.com"
url_nature_articles = "https://www.nature.com/nature/articles?sort=PubDate&year=2020"


def get_request(func):

    def wrapper(url, *args):
        response = requests.get(url)
        if response:
            beautiful_soup = BeautifulSoup(response.content, 'html.parser')
            func_output = func(beautiful_soup, *args)

            return func_output

        print(f"The {url} returned {response.status_code}!")
        return None

    return wrapper


@get_request
def get_article(bs: BeautifulSoup):
    text = bs.find('div', {'class': 'c-article-body'}).text.strip()
    return text


@get_request
def find_articles_on_page(bs: BeautifulSoup, target_type: str, path: str):
    #   TODO Now saving process is placed in this function. Should be moved to find_articles.
    articles_list = bs.find_all('li', {'class': 'app-article-list-row__item'})
    news_dict = dict()
    saved_news = list()

    for article in articles_list:
        article_type = article.find('span', {'class': 'c-meta__type'})
        if article_type and article_type.contents[0] == target_type:
            name = article.find('a').contents[0]
            link = article.find('a').get('href')
            news_dict[name] = url_nature + link

    for name, link in news_dict.items():
        content = get_article(link)
        if content:
            saved_news.append(save_content(name, content, path))

    return saved_news


def prepare_file_name(article_name):
    file_name = article_name.translate({ord(letter): None for letter in string.punctuation})
    file_name = file_name.replace(' ', '_')
    file_name = file_name + '.txt'

    return file_name


def save_content(article_name, content, path):
    file_name = prepare_file_name(article_name)
    path = os.path.join(path, file_name)
    file = open(path, 'wb')
    file.write(content.encode('utf-8'))

    return file_name


def find_articles(url, pages_amount, target_type):
    saved_articles = list()
    parent_dir = os.getcwd()

    for page_number in range(1, pages_amount + 1):
        page_url = url + f"&page{page_number}"
        path = os.path.join(parent_dir, f'Page_{page_number}')
        os.mkdir(path)
        saved_articles.extend(find_articles_on_page(page_url, target_type, path))

    return saved_articles


def main():
    pages_amount = int(input())
    target_type = input()
    print(find_articles(url_nature_articles, pages_amount, target_type))


if __name__ == '__main__':
    main()
