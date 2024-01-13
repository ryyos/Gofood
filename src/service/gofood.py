import requests
import os
import datetime as date

from time import time, sleep
from datetime import datetime, timezone
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
        self.MAIN_PATH = 'data'

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



        match action:

            case 'get':
                retry = 0
                while True:
                    try:
                        response = self.__sessions.get(url=url, headers=self.HEADER)

                        logger.info(f'response status: {response.status_code}')
                        logger.info(f'try request in url: {url}')
                        logger.info(f'request action: {action}')
                        logger.info(f'url review: {url_review}')
                        print()

                        if response.status_code == 200: break

                        sleep(retry_interval)

                        logger.warning(f'response status: {response}')
                        logger.warning(f'retry interval: {retry_interval}')
                        logger.warning(f'retry to: {retry}')
                        print()

                        retry_interval+=5
                        retry+=1

                    except Exception as err:

                        logger.error(err)
                        logger.warning(f'retry interval: {retry_interval}')
                        logger.warning(f'retry to: {retry}')
                        print()

                        sleep(retry_interval)
                        retry_interval+=5

                return response


            case 'post':

                while True:
                    try:
                        response = self.__sessions.post(url=url, headers=self.HEADER, json=payload)

                        logger.info(f'response status: {response.status_code}')
                        logger.info(f'try request in url: {url}')
                        logger.info(f'request action: {action}')
                        logger.info(f'url review: {url_review}')
                        print()

                        if response.status_code == 200: break

                        sleep(retry_interval)
                        retry_interval+=5
                    except Exception as err:
                        logger.error(err)
                        logger.warning(f'retry interval: {retry_interval}')
                        logger.warning(f'retry to: {retry}')

                        sleep(retry_interval)
                        retry_interval+=5

                return response
            
            
            case 'review':

                while True:
                    try:
                        response = self.__sessions.get(url=url, headers=self.HEADER)

                        logger.info(f'response status: {response.status_code}')
                        logger.info(f'try request in url: {url}')
                        logger.info(f'request action: {action}')
                        logger.info(f'url review: {url_review}')
                        print()

                        if response.status_code == 200: break

                        sleep(retry_interval)
                        retry_interval+=5
                        response = self.__sessions.get(url=url_review, headers=self.HEADER)

                    except Exception as err:
                        logger.error(err)
                        logger.warning(f'retry interval: {retry_interval}')
                        logger.warning(f'retry to: {retry}')

                        sleep(retry_interval)
                        retry_interval+=5

                return response

        ...

    def __create_dir(self, raw_data: dict) -> str:

        if not os.path.exists(f'{self.MAIN_PATH}/{raw_data["location_review"]}'): os.mkdir(f'data/{raw_data["location_review"]}')
        if not os.path.exists(f'{self.MAIN_PATH}/{raw_data["location_review"]}/{raw_data["location_restaurant"]["area"]}'): os.mkdir(f'data/{raw_data["location_review"]}/{raw_data["location_restaurant"]["area"]}')
        if not os.path.exists(f'{self.MAIN_PATH}/{raw_data["location_review"]}/{raw_data["location_restaurant"]["area"]}/{file_name(raw_data["reviews_name"].lower())}'): os.mkdir(f'data/{raw_data["location_review"]}/{raw_data["location_restaurant"]["area"]}/{file_name(raw_data["reviews_name"].lower())}')
        if not os.path.exists(f'{self.MAIN_PATH}/{raw_data["location_review"]}/{raw_data["location_restaurant"]["area"]}/{file_name(raw_data["reviews_name"].lower())}/json'): os.mkdir(f'data/{raw_data["location_review"]}/{raw_data["location_restaurant"]["area"]}/{file_name(raw_data["reviews_name"].lower())}/json')
        
        return f'data/{raw_data["location_review"]}/{raw_data["location_restaurant"]["area"]}/{file_name(raw_data["reviews_name"].lower())}/json'
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
        logger.info('extract review from restaurant')
        uid = raw_json["restaurant_id"]

        page = '?page=1&page_size=50'
        response = self.__retry(url=f'{self.API_REVIEW_PAGE}{uid}/reviews{page}')

        page_review = 0
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

                path_data = self.__create_dir(raw_json)

                detail_reviews["tags_review"].append(self.DOMAIN)

                raw_json.update({
                    "detail_reviews": detail_reviews,
                    "path_data_raw": f'{path_data}/{detail_reviews["username_id"]}.json',
                    "path_data_clean": f'{path_data}/{detail_reviews["username_id"]}.json'
                })                

                self.__file.write_json(path=f'{path_data}/{detail_reviews["username_id"]}.json',
                                       content=raw_json)

                
                
            logger.info(f'page review: {page_review}')
            logger.info(f'api review page: {self.API_REVIEW_PAGE}{uid}/reviews{page}')
            print()

            page = response.json().get("next_page", None)
            if page:
                response = self.__retry(url=f'{self.API_REVIEW_PAGE}{uid}/reviews{page}', action='review', url_review=self.__url_food_review)
                page_review+=1

            else: 
                logger.warning(f'review finished')
                break
        ...

    def __fetch_card_food(self, city: str, restaurant: str) -> List[str]:
        response = self.__retry(url=f'https://gofood.co.id/_next/data/8.10.0/id{restaurant}/near_me.json?service_area={city}&locality={restaurant.split("/")[-1]}&category=near_me')
        logger.info('fetch card food')


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

            
            logger.info(f'card page: {page_token}')
            logger.info(f'total card: {len(cards)}')
            print()

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

        cities = response.json()
        for city in cities["pageProps"]["contents"][0]["data"]: # Mengambil Kota
            response = self.__retry(url=f'https://gofood.co.id/_next/data/8.10.0/id/{city["name"].lower()}/restaurants.json')

            for restaurant in response.json()["pageProps"]["contents"][0]["data"]: # Mengambil restaurant dari kota

                cards = self.__fetch_card_food(city=city["name"].lower(), restaurant=restaurant["path"]) # Mengambil card makanan dari restaurant

                for card in cards: # lokasi thread

                    api_review = f'https://gofood.co.id/_next/data/8.10.0/id{card}/reviews.json?id={card.split("/")[-1]}'
                    self.__url_food_review = api_review

                    food_review = self.__retry(api_review)

                    task_executor = []
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


                    logger.info(f'city: {city["name"].lower()}')
                    logger.info(f'restaurant: {restaurant["path"].split("/")[-1]}')
                    logger.info(f'link: {header_required["link"]}')
                    logger.info(f'api review: {api_review}')
                    logger.info(f'restaurant name: {header_required["reviews_name"]}')
                    print()


                    header_required["tags"].append(self.DOMAIN)
                    # self.__extract_restaurant(raw_json=header_required)
                    task_executor.append(self.__executor.submit(self.__extract_restaurant, header_required))

                    sleep(1)

                wait(task_executor)
                self.__executor.shutdown(wait=True)
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