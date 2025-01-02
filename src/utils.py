import os
from datetime import datetime

import pdfkit
from dateutil.relativedelta import relativedelta
import PyPDF2
from sys import platform

month_translation = {
    "janvier": "january",
    "février": "february",
    "mars": "march",
    "avril": "april",
    "mai": "may",
    "juin": "june",
    "juillet": "july",
    "août": "august",
    "septembre": "september",
    "octobre": "october",
    "novembre": "november",
    "décembre": "december",
}

month_translation2 = {
    "jan.": "january",
    "feb.": "february",
    "march": "march",
    "april": "april",
    "may": "may",
    "june": "june",
    "july": "july",
    "aug.": "august",
    "sept.": "september",
    "oct.": "october",
    "nov.": "november",
    "dec.": "december",
}


def parse_date_locale_fr(date_str: str):
    for fr, en in month_translation.items():
        if fr in date_str:
            date_str = date_str.replace(fr, en)
    if "1er" in date_str:
        date_str = date_str.replace("1er", "1")
    date_obj = datetime.strptime(date_str, '%d %B %Y')
    return date_obj


def parse_date_locale_en(date_str: str):
    for fr, en in month_translation.items():
        if fr in date_str:
            date_str = date_str.replace(fr, en)
    if "1er" in date_str:
        date_str = date_str.replace("1er", "1")
    date_obj = datetime.strptime(date_str, '%B %d, %Y')
    return date_obj


def parse_date_locale_en_2(date_str: str):
    for fr, en in month_translation.items():
        if fr in date_str:
            date_str = date_str.replace(fr, en)
    for fr, en in month_translation2.items():
        if fr in date_str:
            date_str = date_str.replace(fr, en)
    if "1er" in date_str:
        date_str = date_str.replace("1er", "1")
    date_obj = datetime.strptime(date_str, '%B %d, %Y')
    return date_obj


def parse_date_locale_fr_wout_day(date_str: str):
    for fr, en in month_translation.items():
        if fr in date_str:
            date_str = date_str.replace(fr, en)
    if "january" in date_str or "march" in date_str or "may" in date_str or "july" in date_str or "august" in date_str or "october" in date_str or "december" in date_str:
        date_str = f"31 {date_str}"
    if "april" in date_str or "june" in date_str or "september" in date_str or "november" in date_str:
        date_str = f"30 {date_str}"
    if "february" in date_str:
        date_str = f"28 {date_str}"
    date_obj = datetime.strptime(date_str, '%d %B %Y')
    return date_obj


def parse_date_iso(date_str: str):
    return datetime.fromisoformat(date_str)


def create_quarter_ranges(start_date, end_date):
    # Parse the input dates
    # start_date = datetime.strptime(start_date, "%d/%m/%Y")
    # end_date = datetime.strptime(end_date, "%d/%m/%Y")
    # Define quarter start months
    quarter_starts = [1, 4, 7, 10]
    # Align the start date with the beginning of its quarter
    current_quarter_start_month = max(
        month for month in quarter_starts if month <= start_date.month
    )
    current_quarter_start = datetime(
        start_date.year, current_quarter_start_month, 1
    )
    if current_quarter_start > start_date:
        current_quarter_start -= relativedelta(months=3)
    # Initialize the list to store quarter ranges
    quarters = []
    # Generate quarters until the end date
    while current_quarter_start < end_date:
        # Calculate the next quarter start date
        next_quarter_start = current_quarter_start + relativedelta(months=3)
        # Add the range to the list
        quarters.append([current_quarter_start, next_quarter_start])
        # Move to the next quarter
        current_quarter_start = next_quarter_start
    # Ensure the last quarter's end date does not exceed the given end_date
    # quarters[-1][1] = min(quarters[-1][1], end_date)
    return [[q[0].timestamp(), q[1].timestamp()] for q in quarters]


def name_quarter(quarter):
    s = datetime.fromtimestamp(quarter[0])
    month = s.month
    year = s.year
    q_number = int(month / 3) + 1
    return f"{str(year)}-T{str(q_number)}"


def write_to_pdf(content: str, file: str):
    wkhtml_path = pdfkit.configuration(
        wkhtmltopdf=os.getenv("WKHTMLTOPDF", "")
    )  # by using configuration you can add path value.
    pdfkit.from_string(content, file, configuration=wkhtml_path)


def write_to_pdf_from_website(url: str, file: str):
    try:
        wkhtml_path = pdfkit.configuration(
            wkhtmltopdf=os.getenv("WKHTMLTOPDF", "")
        )  # by using configuration you can add path value.
        options = {
            '--load-error-handling': 'ignore'
        }
        pdfkit.from_url(url, file, configuration=wkhtml_path, options=options)
        return True
    except Exception as e:
        print(f"Failed to save {url} to {file} as PDF [Error = {e}]")
        return False


def merge_pdf_files(pdfs, output):
    merger = PyPDF2.PdfMerger()
    try:
        for pdf in pdfs:
            merger.append(pdf)
        with open(output, 'wb') as merged_pdf:
            merger.write(merged_pdf)
        merger.close()
    except Exception as e:
        print(e)
        return False
    return True
