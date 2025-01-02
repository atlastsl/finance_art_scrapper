import os
import glob
import json
from datetime import datetime
from utils import write_to_pdf_from_website, merge_pdf_files, write_to_pdf
import tempfile

html_base = """
    <!DOCTYPE html>
    <html>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
    <head>
    <title>Page Title</title>
    </head>
    <body>

    @HTML_PDF

    </body>
    </html>
"""

project_dir = os.path.dirname(os.path.abspath(__file__).replace("\\", "/").replace("/src", ""))


def read_sources():
    directory_path = project_dir + '/files/articles'
    articles_files = glob.glob(os.path.join(directory_path, '*.json'))
    articles = []
    for article_file in articles_files:
        with open(article_file, 'r') as file:
            data = json.load(file)
            articles = articles + data
    return articles


def organize_articles(articles):
    quarters = []
    for article in articles:
        if article['quarter'] not in quarters:
            quarters.append(article['quarter'])
    quarters.sort()
    organized_articles = []
    for quarter in quarters:
        tmp = [article for article in articles if article['quarter'] == quarter]
        q_articles = []
        for article in tmp:
            q_articles = q_articles + article['articles']
        organized_articles.append({"quarter": quarter, "articles": q_articles})
    return organized_articles


def create_main_page(_article):
    html_body = f"""
        <h1>{_article['title']}</h1>
        <h2>{datetime.fromisoformat(_article['date']).strftime('%d/%m/%Y').lower()}</h2>
        <h3>{_article['site']}</h3>
    """
    return html_base.replace("@HTML_PDF", html_body)


def create_quarter_pdf(article):
    pdf_files = []
    if len(article['articles']) > 0:
        for i in range(len(article['articles'])):
            _article = article['articles'][i]
            main_page_filepath = tempfile.mktemp()
            article_filepath = tempfile.mktemp()
            main_page_file = create_main_page(_article)
            write_to_pdf(main_page_file, main_page_filepath)
            write_to_pdf_from_website(_article['url'], article_filepath)
            pdf_files.append(main_page_filepath)
            pdf_files.append(article_filepath)
        output_dir = project_dir + '/files/output'
        output_pdf = output_dir + '/' + article['quarter'] + ".pdf"
        merge_pdf_files(pdf_files, output_pdf)
        for pdf_file in pdf_files:
            os.remove(pdf_file)


if __name__ == '__main__':
    print(project_dir)
    # downloaded_articles = organize_articles(read_sources())
    # started = False
    # for i in range(len(downloaded_articles)):
    #     if not started:
    #         if downloaded_articles[i]['quarter'] == "2002-T1":
    #             started = True
    #         else:
    #             continue
    #     create_quarter_pdf(downloaded_articles[i])
    #     print(f"Done for {downloaded_articles[i]['quarter']}")
