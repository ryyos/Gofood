import requests
import os
import datetime as date

from time import time, sleep
from datetime import datetime, timezone
from icecream import ic
from fake_useragent import FakeUserAgent
from typing import List
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait

from src.utils.fileIO import File
from src.utils.logs import logger
from src.utils.corrector import vname
from src.utils.corrector import file_name

class Gofood:
    def __init__(self) -> None:

        self.__file = File()
        self.__faker = FakeUserAgent(browsers='chrome', os='windows')
        self.__sessions = requests.Session()
        self.__executor = ThreadPoolExecutor(max_workers=10)

        self.DOMAIN = 'gofood.co.id'
        self.MAIN_URL = 'https://gofood.co.id'

        self.API_CITY = 'https://gofood.co.id/_next/data/8.10.0/id/cities.json' # 89
        self.RESTAURANT = 'https://gofood.co.id/_next/data/8.10.0/id/jakarta/restaurants.json' # 94
        self.NEAR_ME_API = 'https://gofood.co.id/_next/data/8.10.0/id/jakarta/bekasi-restaurants/near_me.json' 
        self.FOODS_API = 'https://gofood.co.id/api/outlets'
        self.API_REVIEW = 'https://gofood.co.id/_next/data/8.10.0/id/jakarta/restaurant/mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8/reviews.json?id=mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8'
        self.API_REVIEW_PAGE = 'https://gofood.co.id/api/outlets/'

        self.__url_food_review = ''
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

        self.RATING = {
            "CANNED_RESPONSE_TASTE": "taste",
            "CANNED_RESPONSE_PORTION": "portion",
            "CANNED_RESPONSE_PACKAGING": "packaging",
            "CANNED_RESPONSE_FRESHNESS": "freshness",
            "CANNED_RESPONSE_VALUE": "prices",
            "CANNED_RESPONSE_HYGIENE": "hygiene",
        }
        ...

    def __convert_time(self, times: str) -> int:
        dt = date.datetime.fromisoformat(times)
        dt = dt.replace(tzinfo=timezone.utc) 

        return int(dt.timestamp())
        ...

    def __retry(self, url: str, action: str = 'get', payload: dict = None, retry_interval: int = 10, url_review: str = None):

        ic(url)
        match action:

            case 'get':

                while True:
                    try:
                        response = self.__sessions.get(url=url, headers=self.HEADER)
                        ic(response)
                        if response.status_code == 200: break

                        sleep(retry_interval)
                        retry_interval+=5
                    except Exception as err:
                        ic(err)

                        sleep(retry_interval)
                        retry_interval+=5

                return response


            case 'post':

                while True:
                    try:
                        response = self.__sessions.post(url=url, headers=self.HEADER, json=payload)
                        ic(response)
                        if response.status_code == 200: break

                        sleep(retry_interval)
                        retry_interval+=5
                    except Exception as err:
                        ic(err)

                        sleep(retry_interval)
                        retry_interval+=5

                return response
            
            
            case 'review':

                while True:
                    try:
                        response = self.__sessions.get(url=url, headers=self.HEADER)
                        ic(response)
                        if response.status_code == 200: break

                        sleep(retry_interval)
                        retry_interval+=5
                        response = self.__sessions.get(url=url_review, headers=self.HEADER)

                    except Exception as err:
                        ic(err)

                        sleep(retry_interval)
                        retry_interval+=5

                return response

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
        response = self.__retry(url=f'{self.API_REVIEW_PAGE}{uid}/reviews{page}')

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
                response = self.__retry(url=f'{self.API_REVIEW_PAGE}{uid}/reviews{page}', action='review', url_review=self.__url_food_review)
                ic('next'+ str(response))

            else: break
        ...

    def __fetch_card_food(self, city: str, restaurant: str) -> List[str]:
        response = self.__retry(url=f'https://gofood.co.id/_next/data/8.10.0/id{restaurant}/near_me.json?service_area={city}&locality={restaurant.split("/")[-1]}&category=near_me')


        latitude = response.json()["pageProps"]["userLocation"]["chosenLocation"]["latitude"]
        longitude = response.json()["pageProps"]["userLocation"]["chosenLocation"]["longitude"]

        page_token = 1
        cards = [card["path"] for card in response.json()["pageProps"]["outlets"]]
        while True:

            response = self.__retry(url=self.FOODS_API, 
                                    action='post',
                                    payload=self.__buld_payload(page=page_token, 
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

        response = self.__retry(url=self.API_CITY)
        ic(response)

        cities = response.json()
        for city in cities["pageProps"]["contents"][0]["data"]: # Mengambil Kota
            response = self.__retry(url=f'https://gofood.co.id/_next/data/8.10.0/id/{city["name"].lower()}/restaurants.json')

            for restaurant in response.json()["pageProps"]["contents"][0]["data"]: # Mengambil restaurant dari kota
                ic(restaurant)

                cards = self.__fetch_card_food(city=city["name"].lower(), restaurant=restaurant["path"]) # Mengambil card makanan dari restaurant

                for card in cards: # lokasi thread
                    self.__url_food_review = f'https://gofood.co.id/_next/data/8.10.0/id{card}/reviews.json?id={card.split("/")[-1]}'

                    food_review = self.__retry(f'https://gofood.co.id/_next/data/8.10.0/id{card}/reviews.json?id={card.split("/")[-1]}')
                    ic(food_review)
                    ic(f'https://gofood.co.id/_next/data/8.10.0/id{card}/reviews.json?id={card.split("/")[-1]}')
                    ic(self.MAIN_URL+food_review.json()["pageProps"].get("outletUrl"))

                    header_required = {
                        "link": self.MAIN_URL+food_review.json()["pageProps"].get("outletUrl"),
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
                        },

                        "detail_total_rating": [
                            {
                                "category_rating": self.RATING[rating["id"]],
                                "score_rating": rating["count"]
                            } for rating in food_review.json()["pageProps"]["cannedOutlet"]
                        ],

                        "range_prices": self.PRICE[str(food_review.json()["pageProps"]["outlet"]["priceLevel"])],
                        "restaurant_id": food_review.json()["pageProps"]["outlet"]["uid"],
                        "detail_reviews": ""
                    }

                    header_required["tags"].append(self.DOMAIN)
                    # self.__extract_restaurant(raw_json=header_required)
                    self.__executor.submit(self.__extract_restaurant, header_required)
                    ic("restaurant")

                    sleep(1)

                wait(self.__executor)
                break

            break
        ...

# data/jakarta/bekasi-restaurant/nama_restaurant/review01.json

'https://gofood.co.id/jakarta/restaurants/nasi-goreng-jawa-rawalumbu-070863f9-50b1-4054-b636-db164f267131'
'https://gofood.co.id/jakarta/restaurant/nasi-goreng-jawa-rawalumbu-070863f9-50b1-4054-b636-db164f267131'


'https://gofood.co.id/jakarta/restaurant/mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8/reviews.json?id=mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8'
'https://gofood.co.id/_next/data/8.10.0/id/jakarta/restaurant/mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8/reviews.json?id=mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8'

# https://gofood.co.id/_next/data/8.10.0/id/jakarta/restaurant/waroeng-ikal-3-76-ruko-grand-galaxy-265efdac-fdd0-44c6-bd3f-9564423f61c2/reviews.json?service_area=jakarta&id=waroeng-ikal-3-76-ruko-grand-galaxy-265efdac-fdd0-44c6-bd3f-9564423f61c2
# https://gofood.co.id/_next/data/8.10.0/id/jakarta/restaurant/waroeng-ikal-376-ruko-grand-galaxy-265efdac-fdd0-44c6-bd3f-9564423f61c2/reviews.json?id=waroeng-ikal-376-ruko-grand-galaxy-265efdac-fdd0-44c6-bd3f-9564423f61c2


# https://gofood.co.id/_next/data/8.10.0/id/jakarta/restaurant/a-w-linc-square-d4fe7a94-86cd-4883-b279-07bdd7002ad9/reviews.json?id=a-w-linc-square-d4fe7a94-86cd-4883-b279-07bdd7002ad9
# https://gofood.co.id/_next/data/8.10.0/id/jakarta/restaurant/aw-linc-square-d4fe7a94-86cd-4883-b279-07bdd7002ad9/reviews.json?id=aw-linc-square-d4fe7a94-86cd-4883-b279-07bdd7002ad9


# for card in tqdm(cards, ascii=True, smoothing=0.1, total=len(cards)): # lokasi thread

# data/jakarta/bekasi-restaurants/Ayam_Geprek_Bu_TER_Bekasi_Selatan/json/270871ab-bb07-4f65-8e9d-8c12b0ddcbc5.json