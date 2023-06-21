import requests
from bs4 import BeautifulSoup
import json
from os import path as p, stat
from unidecode import unidecode


class Scraper:
    def __init__(self, path, email, password ):
        self.path = path
        self.email = email
        self.password = password
        self.login_url = 'https://tramites.extranjeria.gob.cl/login'
        self.get_url = 'https://tramites.extranjeria.gob.cl/etapas/inbox'
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'tramites.extranjeria.gob.cl',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

    def normalize(self, d):
        for k, v in d.items():
            d[k] = (unidecode(v[0]), unidecode(v[1]))
        for k in list(d):
            d[unidecode(k).strip()] = d.pop(k)

    def get_login(self):
        # Start a session
        session = requests.Session()

        # get request
        try:
            response = session.get(self.login_url)
        except:
            return '', session

        # parse response for csrf token
        bs = BeautifulSoup(response.text, 'html.parser')
        try:
          csrf_token = bs.find('input', attrs={'name': '_token'})['value']
        except:
            csrf_token = ''
        return csrf_token, session

    def login_and_request(self, csrf, session):
        # Login data
        login_data = {
            'email': self.email,
            'password': self.password,
            '_token': csrf
        }

        # Send a POST request to the login page with the login data
        login_response = session.post(self.login_url, data=login_data)
        if login_response.status_code == '200':
            print('Successful Login')
        return session

    def get_request(self, session):
        # Send a GET request to retrieve the inbox page
        get_inbox_response = session.get(self.get_url, headers=self.headers)
        # print(get_inbox_response.content)
        return get_inbox_response

    def scrape(self, response):
        # Find all table rows
        bs = BeautifulSoup(response.text, 'html.parser')
        table_rows = bs.find_all('tr')
        # print(table_rows)
        return table_rows

    def parse(self, data):
        # Break tr's into td's and organize them to be readable 
        parsed = {}
        for i in range(1, len(data)):
            # Parse each <tr> into a key value pair with the id number as the key and the ref and name in a list as the value
            temp = {data[i].contents[3].contents[0]:(data[i].contents[5].contents[0], data[i].contents[7].contents[0])}
            parsed.update(temp) 

        # print(parsed)
        return parsed

    def append(self, parsed):
        # Open file in append mode, will create file if it doesn't exist
        if p.isfile(self.path):
            f = open(self.path, 'r')
            # Compare obtained info and return new data
            if stat(self.path).st_size != 0:
                #print(f.readlines())
                old_data = json.load(f)
                old_keys = old_data.keys()
                for i in old_keys:
                    if parsed.get(i):
                        parsed.pop(i)
                if parsed == {}:
                    return False
                parsed.update(old_data)
            f.close()
        if parsed != {}:
            f = open(self.path, 'w')
            json.dump(parsed, f, indent=4)
            f.close()
            return True
        else:
            return False
