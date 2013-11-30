# -*- coding: utf-8 -*-

from app.web import PDFDownloader, PDFDownloaderException


def load_raw_pdf(user_data):
    downloader = PDFDownloader(user_data)

    try:
        downloader.load_portal_website()
        raw_pdf = downloader.load_latest_pdf()
    except PDFDownloaderException as error:
        raise BmukSapException('PDF download error. ' + error.message)

    return __decode_pdf(raw_pdf)


def __decode_pdf(string):
    return string


class BmukSapException(Exception):
    pass
