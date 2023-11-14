import datetime
import random
import ssl
import time
import traceback

import cloudscraper
import requests
import warnings

import ua_generator
import web3
from bs4 import BeautifulSoup
from Check_mail import *

from logger import logger

warnings.filterwarnings("ignore", category=DeprecationWarning)



class Nansen:

    def __init__(self, email, password,capKey, proxy,refCode=None):

        self.token, self.csrf_token = None, None
        self.sitekey = '6LcnRGwnAAAAAH-fdJFy0hD3e4GeYxWkMcbkCwi2'

        self.email, self.password, self.capKey, self.refCode = email, password, capKey, refCode
        self.session = self._make_scraper
        self.session.proxies = {"http": f"http://{proxy.split(':')[2]}:{proxy.split(':')[3]}@{proxy.split(':')[0]}:{proxy.split(':')[1]}",
                                "https": f"http://{proxy.split(':')[2]}:{proxy.split(':')[3]}@{proxy.split(':')[0]}:{proxy.split(':')[1]}"}
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        self.session.headers.update({"user-agent": ua_generator.generate().text,
                                     'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'})

    def Registration(self):

        payload = {'_gotcha': '',
                    'email': self.email,
                    'captcha_settings': {"keyname":"google_recaptcha_classic","fallback":"true","orgId":"00D5i0000088WA3","ts":str(datetime.datetime.now().timestamp())},
                    'g-recaptcha-response': self.CaptchaSolver,
                    'submit': 'Join Waitlist'}

        with self.session.post(f'https://getlaunchlist.com/s/yeywGr?ref={self.refCode}', data=payload, allow_redirects=True) as response:

            soup = BeautifulSoup(response.text, 'html.parser')

            # print(soup)

            self.csrf_token = soup.find('meta', attrs={'name': 'csrf-token'}).get('content')
            # print(self.csrf_token)



    def sendMail(self):

        payload = {"email":self.email,
                   "csrf_token":self.csrf_token}

        with self.session.post(f'https://getlaunchlist.com/s/verify/send/{self.email}', json=payload) as response:
            print(response.text)

            link = check_mail(self.email, self.password, 'hello@getlaunchlist.com')
            with self.session.get()

    @property
    def CaptchaSolver(self) -> str:
        from capmonster_python import RecaptchaV2Task

        capmonster = RecaptchaV2Task(self.capKey)
        task_id = capmonster.create_task("https://www.nansen.ai", self.sitekey)
        result = capmonster.join_task_result(task_id)
        # print(result.get("gRecaptchaResponse"))
        return result.get("gRecaptchaResponse")

    @property
    def _make_scraper(self):
        ssl_context = ssl.create_default_context()
        ssl_context.set_ciphers(
            "ECDH-RSA-NULL-SHA:ECDH-RSA-RC4-SHA:ECDH-RSA-DES-CBC3-SHA:ECDH-RSA-AES128-SHA:ECDH-RSA-AES256-SHA:"
            "ECDH-ECDSA-NULL-SHA:ECDH-ECDSA-RC4-SHA:ECDH-ECDSA-DES-CBC3-SHA:ECDH-ECDSA-AES128-SHA:"
            "ECDH-ECDSA-AES256-SHA:ECDHE-RSA-NULL-SHA:ECDHE-RSA-RC4-SHA:ECDHE-RSA-DES-CBC3-SHA:ECDHE-RSA-AES128-SHA:"
            "ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-NULL-SHA:ECDHE-ECDSA-RC4-SHA:ECDHE-ECDSA-DES-CBC3-SHA:"
            "ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA:AECDH-NULL-SHA:AECDH-RC4-SHA:AECDH-DES-CBC3-SHA:"
            "AECDH-AES128-SHA:AECDH-AES256-SHA"
        )
        ssl_context.set_ecdh_curve("prime256v1")
        ssl_context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1_3 | ssl.OP_NO_TLSv1)
        ssl_context.check_hostname = False

        return cloudscraper.create_scraper(
            debug=False,
            ssl_context=ssl_context
        )


if __name__ == '__main__':



    emails = []
    proxy = []


    with open('InputData/Emails.txt', 'r', encoding='utf-8') as file:
        for i in file:
            emails.append([i.rstrip().split(':')[0], i.rstrip().split(':')[1]])

    with open('InputData/Proxy.txt', 'r', encoding='utf-8') as file:
        for i in file:
            proxy.append(i.rstrip())

    count = 0
    while count < len(proxy):

        try:

            # print(check_mail(emails[count][0], emails[count][1], 'hello@getlaunchlist.com'))
            # input()


            acc = Nansen(
                          email = emails[count][0],
                          password = emails[count][1],
                          proxy = proxy[count],
                          capKey = '',
                          refCode = ''
            )

            acc.Registration()
            logger.success(f'{count + 1} - Регистрация пройдена')

            acc.sendMail()
            logger.success(f'{count + 1} - Письмо отправлено')



            print('')


        except Exception as e:

            traceback.print_exc()

            logger.error(f'{count+1} - {str(e)}')

        time.sleep(random.randint(1, 10))
        count+=1

    input('\n\n Скрипт завершил работу, все логи находятся в папке Logs')

