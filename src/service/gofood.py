import requests
import os
import datetime as date

from time import time, sleep
from datetime import datetime, timezone
from icecream import ic
from fake_useragent import FakeUserAgent
from typing import List

from src.utils.fileIO import File
from src.utils.logs import logger
from src.utils.corrector import vname
from src.utils.corrector import file_name

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

        self.PRICE = {
            '0': 'Not Set',
            '1': '<16k',
            '2': '16k-40k',
            '3': '40k-100k',
            '4': '>100k',
        }
        ...

    def __convert_time(self, times: str) -> int:
        dt = date.datetime.fromisoformat(times)
        dt = dt.replace(tzinfo=timezone.utc) 

        return int(dt.timestamp())
        ...

    def __retry(self, url):
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
        return f'/{city}/restaurant/{vname(pieces["core"]["displayName"].lower()).replace("--", "-")}-{pieces["core"]["key"].split("/")[-1]}'
    ...

    def __extract_restaurant(self, raw_json: dict):
        uid = raw_json["restaurant_id"]

        page = '?page=1&page_size=50'
        response = self.__sessions.get(url=f'{self.API_REVIEW_PAGE}{uid}/reviews{page}', headers=self.HEADER)

        ic(f'{self.API_REVIEW_PAGE}{uid}/reviews{page}')
        ic(response)

        while True:

            review = response.json()["data"]
            for comment in review:
                detail_reviews = {
                    "username_id": comment["id"],
                    "username_reviews": comment["author"]["fullName"],
                    "initialName": comment["author"]["initialName"],
                    "image_reviews": comment["author"]["avatarUrl"],
                    "created_time": comment["createdAt"],
                    "created_time_epoch": self.__convert_time(comment["createdAt"]),
                    "reviews_rating": comment["rating"],
                    "orders": comment["order"],
                    "tags_review": comment["tags"],
                    "content_reviews": comment["text"],
                    "date_of_experience": "",
                }


                detail_reviews["tags_review"].append(self.DOMAIN)

                raw_json.update({
                    "detail_reviews": detail_reviews,
                    "path_data_raw": f'data/{raw_json["location_review"]}/{raw_json["location_restaurant"]["area"]}/{file_name(raw_json["reviews_name"])}/json/{detail_reviews["username_id"]}.json',
                    "path_data_clean": f'data/{raw_json["location_review"]}/{raw_json["location_restaurant"]["area"]}/{file_name(raw_json["reviews_name"])}/json/{detail_reviews["username_id"]}.json',
                })

                if not os.path.exists(f'data/{raw_json["location_review"]}'): os.mkdir(f'data/{raw_json["location_review"]}')
                if not os.path.exists(f'data/{raw_json["location_review"]}/{raw_json["location_restaurant"]["area"]}'): os.mkdir(f'data/{raw_json["location_review"]}/{raw_json["location_restaurant"]["area"]}')
                if not os.path.exists(f'data/{raw_json["location_review"]}/{raw_json["location_restaurant"]["area"]}/{file_name(raw_json["reviews_name"].lower())}'): os.mkdir(f'data/{raw_json["location_review"]}/{raw_json["location_restaurant"]["area"]}/{file_name(raw_json["reviews_name"].lower())}')
                if not os.path.exists(f'data/{raw_json["location_review"]}/{raw_json["location_restaurant"]["area"]}/{file_name(raw_json["reviews_name"].lower())}/json'): os.mkdir(f'data/{raw_json["location_review"]}/{raw_json["location_restaurant"]["area"]}/{file_name(raw_json["reviews_name"].lower())}/json')
                

                self.__file.write_json(path=f'data/{raw_json["location_review"]}/{raw_json["location_restaurant"]["area"]}/{file_name(raw_json["reviews_name"])}/json/{detail_reviews["username_id"]}.json',
                                       content=raw_json)


            page = response.json().get("next_page", None)
            if page:
                sleep(2)
                response = self.__sessions.get(url=f'{self.API_REVIEW_PAGE}/{uid}/reviews{page}', headers=self.HEADER)
                ic('next'+ str(response))

            else: break
        ...

    def __fetch_card_food(self, city: str, restaurant: str) -> List[str]:
        response = self.__sessions.get(url=f'https://gofood.co.id/_next/data/8.10.0/id{restaurant}/near_me.json?service_area={city}&locality={restaurant.split("/")[-1]}&category=near_me', headers=self.HEADER)


        latitude = response.json()["pageProps"]["userLocation"]["chosenLocation"]["latitude"]
        longitude = response.json()["pageProps"]["userLocation"]["chosenLocation"]["longitude"]

        page_token = 1
        cards = [card["path"] for card in response.json()["pageProps"]["outlets"]]
        while True:

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

                for card in cards: # lokasi thread

                    food_review = self.__sessions.get(f'https://gofood.co.id/_next/data/8.10.0/id{card}/reviews.json?id={card.split("/")[-1]}', headers=self.HEADER)
                    ic(food_review)
                    ic(f'https://gofood.co.id/_next/data/8.10.0/id{card}/reviews.json?id={card.split("/")[-1]}')

                    header_required = {
                        "link": self.MAIN_URL+food_review.json()["pageProps"]["outletUrl"],
                        "domain": self.DOMAIN,
                        "tags": [tag["displayName"] for tag in food_review.json()["pageProps"]["outlet"]["core"]["tags"]],
                        "crawling_time": str(datetime.now()),
                        "crawling_time_epoch": int(time()),
                        "path_data_raw": "",
                        "path_data_clean": "",
                        "reviews_name": food_review.json()["pageProps"]["outlet"]["core"]["displayName"],
                        "location_review": city["name"].lower(),

                        "location_restaurant": {
                            "city": city["name"].lower(),
                            "area": restaurant["path"].split("/")[-1],
                            "distance_km": food_review.json()["pageProps"]["outlet"]["delivery"]["distanceKm"],
                        },

                        "range_prices": self.PRICE[str(food_review.json()["pageProps"]["outlet"]["priceLevel"])],
                        "restaurant_id": food_review.json()["pageProps"]["outlet"]["uid"],
                        "category_reviews": "food & baverage",
                        
                        "reviews_rating": {
                            "total_ratings": food_review.json()["pageProps"]["outlet"]["ratings"],
                            "detail_total_rating": [
                                {
                                    "score_rating": food_review.json()["pageProps"]["cannedOutlet"][0]["count"],
                                    "category_rating": "taste",
                                },
                                {
                                    "score_rating": food_review.json()["pageProps"]["cannedOutlet"][1]["count"],
                                    "category_rating": "portion",
                                },
                                {
                                    "score_rating": food_review.json()["pageProps"]["cannedOutlet"][-1]["count"],
                                    "category_rating": "packaging",
                                }
                            ] if len(food_review.json()["pageProps"]["cannedOutlet"]) else None
                        },

                        "range_prices": self.PRICE[str(food_review.json()["pageProps"]["outlet"]["priceLevel"])],
                        "restaurant_id": food_review.json()["pageProps"]["outlet"]["uid"],
                        "detail_reviews": ""
                    }

                    header_required["tags"].append(self.DOMAIN)
                    self.__extract_restaurant(raw_json=header_required)
                    ic("restaurant")

                    sleep(1)

                break

            break
        ...

# data/jakarta/bekasi-restaurant/nama_restaurant/review01.json

'https://gofood.co.id/jakarta/restaurants/nasi-goreng-jawa-rawalumbu-070863f9-50b1-4054-b636-db164f267131'
'https://gofood.co.id/jakarta/restaurant/nasi-goreng-jawa-rawalumbu-070863f9-50b1-4054-b636-db164f267131'


'https://gofood.co.id/jakarta/restaurant/mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8/reviews.json?id=mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8'
'https://gofood.co.id/_next/data/8.10.0/id/jakarta/restaurant/mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8/reviews.json?id=mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8'


"""
ic| response: <Response [200]>
Traceback (most recent call last):
  File "D:\programming\Python\project\Gofood\main.py", line 5, in <module>
    go.main()
  File "D:\programming\Python\project\Gofood\src\service\gofood.py", line 223, in main
    self.__extract_restaurant(raw_json=header_required)
  File "D:\programming\Python\project\Gofood\src\service\gofood.py", line 107, in __extract_restaurant
    "path_data_raw": f'/data/{raw_json["city"]}/{raw_json["area"]}/{file_name(raw_json["reviews_name"].lower())}/json',
                              ~~~~~~~~^^^^^^^^
KeyError: 'city'
PS D:\programming\Py"""

# https://gofood.co.id/_next/data/8.10.0/id/jakarta/restaurant/a-w-linc-square-d4fe7a94-86cd-4883-b279-07bdd7002ad9/reviews.json?id=a-w-linc-square-d4fe7a94-86cd-4883-b279-07bdd7002ad9
# https://gofood.co.id/_next/data/8.10.0/id/jakarta/restaurant/aw-linc-square-d4fe7a94-86cd-4883-b279-07bdd7002ad9/reviews.json?id=aw-linc-square-d4fe7a94-86cd-4883-b279-07bdd7002ad9