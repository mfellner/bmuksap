# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib
import re

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0'

PROTOCOL = 'https://'
LOGIN = 'signon.portal.at'
LOGIN_URL = PROTOCOL + LOGIN + '/siteminderagent/forms/NeuBasicLogin.fcc'
PORTAL = 'pmsappb1.portal.at'
PORTAL_URL = PROTOCOL + PORTAL + '/irj/portal'
RESOURCES = '/webdynpro/resources/sap.com'
PAGE_BUILDER = '/pb/PageBuilder'
OUTPUT_PDF = 'myfile.pdf'


class PDFDownloader:
    def __init__(self, user_data):
        self.user_data = user_data
        self.cookiejar = cookielib.CookieJar()

        handlers = [
            urllib2.HTTPHandler(),
            urllib2.HTTPSHandler(),
            urllib2.HTTPCookieProcessor(self.cookiejar)
        ]

        self.opener = urllib2.build_opener(*handlers)

    def __open_url(self, url, parameters=None):
        headers = {'Accept': 'text/plain, text/html',
                   'User-Agent': USER_AGENT}

        if parameters is not None:
            headers.update({'Content-type': 'application/x-www-form-urlencoded'})
            request = urllib2.Request(url, parameters, headers)
        else:
            request = urllib2.Request(url, headers=headers)
        return self.opener.open(request)

    def __get_url_parameters(self, url):
        parameters = url.split('?')[1]
        parameters = parameters.split('&')
        result = {}
        for parameter in parameters:
            pair = parameter.split('=')
            result[pair[0]] = pair[1]
        return result

    def __get_cookie_value(self, cookie):
        try:
            return self.cookiejar._cookies[PORTAL]['/'][cookie].value
        except KeyError:
            return ''

    def load_portal_website(self):
        # GET portal page, expect redirect to login page.
        try:
            result = self.__open_url(PORTAL_URL)
        except urllib2.URLError as error:
            raise PDFDownloaderException(error.message)

        response_url = result.geturl()

        if LOGIN in response_url:
            login_url = urllib2.unquote(response_url)
            additional_parameters = self.__get_url_parameters(login_url)
        else:
            raise PDFDownloaderException('Unexpected URL ' + response_url)

        try:
            login_parameters = {
                'SMENC': 'UTF-8',
                'Submit': 'SignOn',
                'PASSWORD': self.user_data['password'],
                'USER': self.user_data['username'] + '@' + self.user_data['domain'],
                'USERT1': self.user_data['username'],
                'mydomain': self.user_data['domain'],
                'smauthreason': '',
                'smquerydata': '',
                'target': PORTAL_URL
            }
        except KeyError as error:
            raise PDFDownloaderException(error.message)

        login_parameters.update(additional_parameters)
        parameters = urllib.urlencode(login_parameters)

        # POST login page with parameters.
        try:
            self.__open_url(LOGIN_URL, parameters)
        except urllib2.URLError as error:
            raise PDFDownloaderException(error.message)

        # GET portal page.
        try:
            self.__open_url(PORTAL_URL)
        except urllib2.URLError as error:
            raise PDFDownloaderException(error.message)

    def load_latest_pdf(self):
        cookie_value = self.__get_cookie_value('JSESSIONID')

        if cookie_value != '':
            jsession_id = re.search(r'(.+_SAP).+', cookie_value).group(1)
            site_url = PROTOCOL + PORTAL + RESOURCES + PAGE_BUILDER + ';jsessionid=' + jsession_id
        else:
            raise PDFDownloaderException('No JSESSIONID cookie.')

        parameters = urllib.urlencode({
            'DynamicParameter': '',
            'HistoryMode': '0',
            'NavMode': '0',
            'NavigationTarget': (
                'ROLES://portal_content/PMSAP/at.gv.brz.pmsap.ess.bp_folder/at.gv.brz.pmsap.ess.roles' +
                '/at.gv.brz.pmsap.ess.employee_self_service/com.sap.pct.erp.ess.employee_self_service' +
                '/com.sap.pct.erp.ess.area_benefits_payment/com.sap.pct.erp.ess.paycheck'),
            'PagePath': ('pcd:portal_content/PMSAP/at.gv.brz.pmsap.ess.bp_folder/at.gv.brz.pmsap.ess.roles' +
                         '/at.gv.brz.pmsap.ess.employee_self_service/com.sap.pct.erp.ess.employee_self_service' +
                         '/com.sap.pct.erp.ess.area_benefits_payment/com.sap.pct.erp.ess.paycheck')
        })

        # POST page with PDF file.
        try:
            result = self.__open_url(site_url, parameters)
            content = result.read()
        except urllib2.URLError as error:
            raise PDFDownloaderException(error.message)

        # Parse PDF URL from page.
        pdf_url = PROTOCOL + PORTAL + '/' + re.search(r'\ssrc="/?(\S+\.pdf\S+)"\s', content).group(1)

        for s in RESOURCES.strip('/').split('/'):
            pdf_url = pdf_url.replace('..', s, 1)
            if not '..' in pdf_url:
                break

        # GET and return PDF file.
        try:
            result = self.__open_url(pdf_url)
        except urllib2.URLError as error:
            raise PDFDownloaderException(error.message)

        return result.read()


class PDFDownloaderException(Exception):
    pass
