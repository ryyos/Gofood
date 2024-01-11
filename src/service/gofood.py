import requests

from time import time
from datetime import datetime
from icecream import ic
from fake_useragent import FakeUserAgent

from src.utils.fileIO import File
from src.utils.logs import logger

class Gofood:
    def __init__(self) -> None:

        self.__file = File()
        self.__faker = FakeUserAgent()

        self.DOMAIN = 'gofood.co.id'
        self.MAIN_URL = 'https://gofood.co.id/'
        self.LANGUAGE = 'id'
        self.API_CITY = 'https://gofood.co.id/_next/data/8.10.0/en/jakarta/restaurants.json?service_area='

        self.HEADER = {
            "User-Agent": self.__faker.random
        }
        ...

    def __extract_city(self, url: str) -> None:
        ...

    def main(self, city: str = 'jakarta') -> None:

        response = requests.get(url=self.API_CITY+city, headers=self.HEADER)
        ic(response)

        cities = response.json()
        self.__file.write_json(path='data/cities.json', content=cities)

        for city in cities["pageProps"]["contents"][0]["data"]:
            ic(city)

            break
        ...