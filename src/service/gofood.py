import requests

from time import time, sleep
from datetime import datetime
from icecream import ic
from fake_useragent import FakeUserAgent

from src.utils.fileIO import File
from src.utils.logs import logger
from src.utils.corrector import vname

class Gofood:
    def __init__(self) -> None:

        self.__file = File()
        self.__faker = FakeUserAgent(browsers='chrome', os='windows')

        self.__sessions = requests.Session()

        self.DOMAIN = 'gofood.co.id'
        self.MAIN_URL = 'https://gofood.co.id'
        self.LANGUAGE = 'id'

        self.API_CITY = 'https://gofood.co.id/_next/data/8.10.0/id/cities.json' # 89
        self.RESTAURANT = 'https://gofood.co.id/_next/data/8.10.0/id/jakarta/restaurants.json' # 94
        self.NEAR_ME_API = 'https://gofood.co.id/_next/data/8.10.0/id/jakarta/bekasi-restaurants/near_me.json'

        self.FOODS_API = 'https://gofood.co.id/api/outlets'

        self.HEADER = {
            "User-Agent": self.__faker.random,
            "Content-Type": "application/json"
        }
        ...


    def __buld_payload(self, page: str, latitude: float, longitude: float) -> dict:
        return {
            "code": "NEAR_ME",
            "country_code": "ID",
            "language": "id",
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "pageSize": 12,
            "pageToken": str(page),
            "timezone": "Asia/Jakarta"
        }

    def __create_card(self, city: str, pieces: dict) -> str:
        return f'{self.MAIN_URL}/{city}/restaurant/{vname(pieces["core"]["displayName"].lower())}-{pieces["core"]["key"].split("/")[-1]}'

    def __extract_restaurant(self, city: str, restaurant: str) -> None:
        ic(f'https://gofood.co.id/_next/data/8.10.0/id{restaurant}/near_me.json?service_area={city}&locality={restaurant.split("/")[-1]}&category=near_me')

        response = self.__sessions.get(url=f'https://gofood.co.id/_next/data/8.10.0/id{restaurant}/near_me.json?service_area={city}&locality={restaurant.split("/")[-1]}&category=near_me', headers=self.HEADER)
        ic(response)

        cards = [self.MAIN_URL+card["path"] for card in response.json()["pageProps"]["outlets"]]

        latitude = response.json()["pageProps"]["userLocation"]["chosenLocation"]["latitude"]
        longitude = response.json()["pageProps"]["userLocation"]["chosenLocation"]["longitude"]

        ic(cards)
        page_token = 1
        while True:

            ic(self.__buld_payload(page=page_token, 
                                    latitude=latitude,
                                    longitude=longitude
                                    ))
            response = self.__sessions.post(url=self.FOODS_API, 
                                     headers=self.HEADER, 
                                     json=self.__buld_payload(page=page_token, 
                                                              latitude=latitude,
                                                              longitude=longitude
                                                              ))
            
            ic(response)
            card = [self.__create_card(city=city, pieces=card) for card in response.json()["outlets"]]
            ic(card)
            cards.append()
            try:
                page_token = response.json()["nextPageToken"]
                ic(cards)
                sleep(10)
            except Exception:
                break
        ...

    def main(self) -> None:

        response = self.__sessions.get(url=self.API_CITY, headers=self.HEADER)
        ic(response)

        cities = response.json()
        for city in cities["pageProps"]["contents"][0]["data"]: # Mengambil Kota
            response = self.__sessions.get(url=f'https://gofood.co.id/_next/data/8.10.0/id/{city["name"].lower()}/restaurants.json', headers=self.HEADER)
            ic(city)

            for restaurant in response.json()["pageProps"]["contents"][0]["data"]: # Mengambil restaurant dari kota
                ic(restaurant)
                self.__extract_restaurant(city=city["name"].lower(), restaurant=restaurant["path"])

                break

            break
        ...


# https://gofood.co.id/_next/data/8.10.0/id//jakarta/restaurants/near_me.json?service_area=jakarta&locality=restaurants&category=near_me
# https://gofood.co.id/_next/data/8.10.0/id//jakarta/restaurants/near_me.json?service_area=jakarta&locality=restaurants&category=near_me



'https://gofood.co.id/jakarta/restaurants/nasi-goreng-jawa-rawalumbu-070863f9-50b1-4054-b636-db164f267131'
'https://gofood.co.id/jakarta/restaurant/nasi-goreng-jawa-rawalumbu-070863f9-50b1-4054-b636-db164f267131'