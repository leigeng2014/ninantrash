# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2015/05/27
#
"""Car monitor for tongda OA"""
import requests
import re


class BaseHTTPHandler(object):

    """Base HTTP request handler"""

    def __init__(self, *args, **kwargs):
        self.cookies = ''
        pass

    def _request(self,
                 url=None,
                 method=None,
                 headers=None,
                 files=None,
                 data=None,
                 params=None,
                 auth=None,
                 cookies=None,
                 hooks=None,
                 verify=False):

        headers = self.headers if headers is None else headers
        cookies = self.cookies if cookies is None else cookies

        resp = requests.request(method=method, url=url, params=params,
                                data=data,
                                headers=headers, cookies=cookies,
                                verify=verify, files=files, auth=auth)
        self.cookies = resp.cookies
        return resp


class TongdaOA(BaseHTTPHandler):

    """Tongda OA client."""

    def __init__(self, username="", password=""):
        self.username = username
        self.password = password

        self.host = ''
        self.base_url = 'http://{}/'.format(self.host)

        self.headers = {
            'Accept': '*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Referer': self.base_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 9.1;) Firefox/38.0',
        }
        self.cookies = ''
        self.try_login = self.login()
        if not self.try_login:
            print 'Login Failed.Exit.'
            exit()

    def login(self):
        data = {
            'UNAME': self.username.encode('gbk'),
            'PASSWORD': self.password,
            'submit': u'登 录'.encode('gbk')
        }
        self.login_url = '{}logincheck.php'.format(self.base_url)
        pattern = r'location="./general/"'

        resp = self._request(self.login_url, data=data, method='POST')
        if re.search(pattern, resp.content):
            return True
        return False

    def search_car(self, pattern):
        self.html = ''
        url = '{}general/news/show/Searchcar.php'.format(self.base_url)
        resp = self._request(url, method='GET')
        html = resp.content
        if re.search(pattern, html):
            self.html = html.decode('gbk').encode('utf-8')
            return True
        return False


if __name__ == "__main__":
    tongda = TongdaOA(u'', '')
    pattern = ur'济南'.encode('gbk')
    tongda.search_car(pattern)
