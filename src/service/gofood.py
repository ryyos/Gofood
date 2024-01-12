import requests

from time import time, sleep
from datetime import datetime
from icecream import ic
from fake_useragent import FakeUserAgent
from typing import List

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

        self.API_CITY = 'https://gofood.co.id/_next/data/8.10.0/id/cities.json' # 89
        self.RESTAURANT = 'https://gofood.co.id/_next/data/8.10.0/id/jakarta/restaurants.json' # 94
        self.NEAR_ME_API = 'https://gofood.co.id/_next/data/8.10.0/id/jakarta/bekasi-restaurants/near_me.json' 
        self.FOODS_API = 'https://gofood.co.id/api/outlets'
        self.API_REVIEW = 'https://gofood.co.id/_next/data/8.10.0/id/jakarta/restaurant/mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8/reviews.json?id=mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8'
        self.API_REVIEW_PAGE = 'https://gofood.co.id/api/outlets/'

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
    ...

    def __create_card(self, city: str, pieces: dict) -> str:
        return f'/{city}/restaurant/{vname(pieces["core"]["displayName"].lower())}-{pieces["core"]["key"].split("/")[-1]}'
    ...

    def __extract_food(self, raw_json: dict):
        uid = raw_json["restaurant_id"]

        page = '?page=1&page_size=50'
        response = self.__sessions.get(url=f'{self.API_REVIEW_PAGE}/{uid}/reviews{page}', headers=self.HEADER)
        ic(response)

        while True:
            review = response.json()["data"]

            for comment in review:
                results = {
                    "posted": comment["createdAt"],
                    "user_id": comment["id"],
                    "rating_given": comment["rating"],
                    "tags": comment["tags"],
                    "order": comment["order"],
                    "comment": comment["text"],
                }

                raw_json.update({
                    "user": comment["author"],
                    "review": results
                })

                self.__file.write_json('data/try1.json', raw_json)

                break


            try:
                page = response.json()["next_page"]
                response = self.__sessions.get(url=f'{self.API_REVIEW_PAGE}/{uid}/reviews{page}', headers=self.HEADER)
                break

            except Exception:
                break
        ...

    def __fetch_card_food(self, city: str, restaurant: str) -> List[str]:
        response = self.__sessions.get(url=f'https://gofood.co.id/_next/data/8.10.0/id{restaurant}/near_me.json?service_area={city}&locality={restaurant.split("/")[-1]}&category=near_me', headers=self.HEADER)


        latitude = response.json()["pageProps"]["userLocation"]["chosenLocation"]["latitude"]
        longitude = response.json()["pageProps"]["userLocation"]["chosenLocation"]["longitude"]

        page_token = 1
        cards = [card["path"] for card in response.json()["pageProps"]["outlets"]]
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

            card = [self.__create_card(city=city, pieces=card) for card in response.json()["outlets"]]
            cards.extend(card)
            try:
                page_token = response.json()["nextPageToken"]
                sleep(3)
                ic(cards)
                break
            except Exception:
                break

        return cards
        ...

    def main(self) -> None:

        response = self.__sessions.get(url=self.API_CITY, headers=self.HEADER)
        ic(response)

        cities = response.json()
        for city in cities["pageProps"]["contents"][0]["data"]: # Mengambil Kota
            response = self.__sessions.get(url=f'https://gofood.co.id/_next/data/8.10.0/id/{city["name"].lower()}/restaurants.json', headers=self.HEADER)

            for restaurant in response.json()["pageProps"]["contents"][0]["data"]: # Mengambil restaurant dari kota
                ic(restaurant)

                cards = self.__fetch_card_food(city=city["name"].lower(), restaurant=restaurant["path"]) # Mengambil card makanan dari restaurant

                for card in cards:
                    print(f'https://gofood.co.id/_next/data/8.10.0/id{card}/reviews.json?id={card.split("/")[-1]}')

                    food_review = self.__sessions.get(f'https://gofood.co.id/_next/data/8.10.0/id{card}/reviews.json?id={card.split("/")[-1]}', headers=self.HEADER)
                    ic(food_review)

                    header_required = {
                        "domain": self.DOMAIN,
                        "crawling_time": str(datetime.now()),
                        "crawling_time_epoch": int(),

                        "url": self.MAIN_URL+food_review.json()["pageProps"]["outletUrl"],
                        "ratings": food_review.json()["pageProps"]["outlet"]["ratings"],
                        "distance": food_review.json()["pageProps"]["outlet"]["delivery"]["distanceKm"],
                        "range_prices": food_review.json()["pageProps"]["outlet"]["priceLevel"],
                        "restaurant_name": food_review.json()["pageProps"]["outlet"]["core"]["displayName"],
                        "restaurant_id": food_review.json()["pageProps"]["outlet"]["uid"],

                        "taste_rating": food_review.json()["pageProps"]["cannedOutlet"][0]["count"],
                        "portion_rating": food_review.json()["pageProps"]["cannedOutlet"][1]["count"],
                        "packaging_rating": food_review.json()["pageProps"]["cannedOutlet"][-1]["count"],
                        "review": ""
                    }

                    self.__extract_food(raw_json=header_required)

                    break

                break

            break
        ...

# data/jakarta/bekasi-restaurant/nama_makanan/review01.json

'https://gofood.co.id/jakarta/restaurants/nasi-goreng-jawa-rawalumbu-070863f9-50b1-4054-b636-db164f267131'
'https://gofood.co.id/jakarta/restaurant/nasi-goreng-jawa-rawalumbu-070863f9-50b1-4054-b636-db164f267131'


'https://gofood.co.id/jakarta/restaurant/mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8/reviews.json?id=mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8'
'https://gofood.co.id/_next/data/8.10.0/id/jakarta/restaurant/mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8/reviews.json?id=mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8'