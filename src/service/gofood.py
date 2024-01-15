import os
import datetime as date

from requests import Session
from time import time, sleep, strftime
from datetime import datetime, timezone
from icecream import ic
from tqdm import tqdm
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
        self.__sessions = Session()
        self.__executor = ThreadPoolExecutor(max_workers=5)

        self.__char: str = []
        self.__city: dict = {}

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
        self.HEADER = {"User-Agent": self.__faker.random}

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

    def __retry(self, url: str, 
                action: str = 'get', 
                payload: dict = None, 
                retry_interval: int = 10,
                url_review: str = None
                ):


        match action:

            case 'get':
                retry = 0
                while True:
                    try:
                        response = self.__sessions.get(url=url, headers={"User-Agent": self.__faker.random})

                        logger.info(f'response status: {response.status_code}')
                        logger.info(f'try request in url: {url}')
                        logger.info(f'request action: {action}')
                        logger.info(f'url review: {url_review}')
                        print()

                        if response.status_code == 200: break
                        if response.status_code == 500: return False
                        if response.status_code == 403: self.__sessions = Session()

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

                retry = 0
                while True:
                    try:
                        response = self.__sessions.post(url=url, headers={"User-Agent": self.__faker.random}, json=payload)

                        logger.info(f'response status: {response.status_code}')
                        logger.info(f'try request in url: {url}')
                        logger.info(f'request action: {action}')
                        logger.info(f'url review: {url_review}')
                        print()

                        if response.status_code == 200: return response
                        if response.status_code == 400: return False
                        if response.status_code == 403: self.__sessions = Session()

                        logger.warning(f'retry interval: {retry_interval}')
                        logger.warning(f'retry to: {retry}')
                        logger.warning(f'response status: {response}')
                        
                        sleep(retry_interval)
                        retry_interval+=5
                    except Exception as err:
                        logger.error(err)
                        logger.warning(f'retry interval: {retry_interval}')
                        logger.warning(f'response status: {response}')
                        logger.warning(f'retry to: {retry}')
                        retry+=1

                        sleep(retry_interval)
                        retry_interval+=5

            
            
            case 'review':
                retry = 0
                while True:
                    try:
                        response = self.__sessions.get(url=url, headers={"User-Agent": self.__faker.random})

                        logger.info(f'response status: {response.status_code}')
                        logger.info(f'try request in url: {url}')
                        logger.info(f'request action: {action}')
                        logger.info(f'url review: {url_review}')
                        print()

                        if response.status_code == 200: return response
                        if response.status_code == 500: return False

                        logger.warning(f'retry interval: {retry_interval}')
                        logger.warning(f'retry to: {retry}')
                        logger.warning(f'response status: {response}')

                        sleep(retry_interval)
                        retry_interval+=5
                        retry+=1

                        if response.status_code == 403: self.__sessions = Session()
                        response = self.__sessions.get(url=url_review, headers={"User-Agent": self.__faker.random})

                    except Exception as err:
                        logger.error(err)
                        logger.warning(f'retry interval: {retry_interval}')
                        logger.warning(f'retry to: {retry}')
                        logger.warning(f'response status: {response}')
                        retry+=1

                        sleep(retry_interval)
                        retry_interval+=5

        ...

    def __create_dir(self, raw_data: dict) -> str:
        try: os.makedirs(f'{self.MAIN_PATH}/data_raw/data_review_gofood/{raw_data["location_review"]}/{raw_data["location_restaurant"]["area"]}/{file_name(raw_data["reviews_name"].lower())}/json')
        except Exception: ...
        finally: return f'{self.MAIN_PATH}/data_raw/data_review_gofood/{raw_data["location_review"]}/{raw_data["location_restaurant"]["area"]}/{file_name(raw_data["reviews_name"].lower())}/json'
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

    def __convert_path(self, path: str) -> str:
        
        path = path.split('/')
        path[1] = 'data_clean'
        return '/'.join(path)
        ...

    def __get_review(self, raw_json: dict):
        logger.info('extract review from restaurant')
        uid = raw_json["restaurant_id"]

        page = ''
        response = self.__retry(url=f'{self.API_REVIEW_PAGE}{uid}/reviews{page}')

        page_review = 0
        all_reviews = []
        while True:

            reviews = response.json()["data"]
            for review in reviews: all_reviews.append(review)
                
            logger.info(f'page review: {page_review}')
            logger.info(f'api review page: {self.API_REVIEW_PAGE}{uid}/reviews{page}')
            print()

            page = response.json().get("next_page", None)
            if page:
                response = self.__retry(url=f'{self.API_REVIEW_PAGE}{uid}/reviews{page}', action='review', url_review=self.__url_food_review)
                if not response: break
                page_review+=1

            else: 
                logger.warning(f'review finished')
                break

        raw_json["total_reviews"] = len(all_reviews)
        for comment in tqdm(all_reviews, ascii=True, smoothing=0.1, total=len(all_reviews)):
            detail_reviews = {
                "username_id": comment["id"],
                "username_reviews": comment["author"]["fullName"],
                "initialName": comment["author"]["initialName"],
                "image_reviews": comment["author"]["avatarUrl"],
                "created_time": comment["createdAt"].split('.')[0].replace('T', ' '),
                "created_time_epoch": self.__convert_time(comment["createdAt"]),
                "email_reviews": None,
                "company_name": None,
                "location_reviews": None,
                "title_detail_reviews": None,
                "reviews_rating": comment["rating"],
                "detail_reviews_rating": [{
                    "score_rating": None,
                    "category_rating": None
                }],
                "total_likes_reviews": None,
                "total_dislikes_reviews": None,
                "total_reply_reviews": None,
                "orders": comment["order"],
                "tags_review": comment["tags"],
                "content_reviews": comment["text"],
                "reply_content_reviews": {
                    "username_reply_reviews": None,
                    "content_reviews": None
                },
                "date_of_experience": comment["createdAt"].split('.')[0].replace('T', ' '),
                "date_of_experience_epoch": self.__convert_time(comment["createdAt"]),
            }

            path_data = self.__create_dir(raw_data=raw_json)

            detail_reviews["tags_review"].append(self.DOMAIN)

            raw_json.update({
                "detail_reviews": detail_reviews,
                "path_data_raw": f'{path_data}/{detail_reviews["username_id"]}.json',
                "path_data_clean": f'{self.__convert_path(path_data)}/{detail_reviews["username_id"]}.json'
            })                

            self.__file.write_json(path=f'{path_data}/{detail_reviews["username_id"]}.json',
                                    content=raw_json)   
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

            if not response: break
            card = [self.__create_card(city=city, pieces=card) for card in response.json()["outlets"]]
            cards.extend(card)

            
            logger.info(f'card page: {page_token}')
            logger.info(f'total card: {len(cards)}')
            print()

            try:
                page_token = response.json()["nextPageToken"]
                if page_token == '': break

            except Exception as err:
                ic(err)
                break

        return cards
        ...

    def __extract_restaurant(self, restaurant: dict):
            cards = self.__fetch_card_food(city=self.__city["name"].lower(), restaurant=restaurant["path"]) # Mengambil card makanan dari restaurant

            for index, card in enumerate(cards):

                api_review = f'https://gofood.co.id/_next/data/8.10.0/id{card}/reviews.json?id={card.split("/")[-1]}'
                
                try: 
                    self.__url_food_review = api_review.replace('--', '-')

                    logger.info(card)
                    food_review = self.__retry(api_review.replace('--', '-'))

                    header_required = {
                        "link": self.MAIN_URL+food_review.json()["pageProps"].get("outletUrl"),
                        "domain": self.DOMAIN,
                        "tags": [tag["displayName"] for tag in food_review.json()["pageProps"]["outlet"]["core"]["tags"]],
                        "crawling_time": strftime('%Y-%m-%d %H:%M:%S'),
                        "crawling_time_epoch": int(time()),
                        "path_data_raw": "",
                        "path_data_clean": "",
                        "reviews_name": food_review.json()["pageProps"]["outlet"]["core"]["displayName"],
                        "location_review": self.__city["name"].lower(),
                        "category_reviews": "food & baverage",
                        "total_reviews": 0,

                        "location_restaurant": {
                            "city": self.__city["name"].lower(),
                            "area": restaurant["path"].split("/")[-1],
                            "distance_km": food_review.json()["pageProps"]["outlet"]["delivery"]["distanceKm"],
                        },

                        "range_prices": self.PRICE[str(food_review.json()["pageProps"]["outlet"]["priceLevel"])],
                        "restaurant_id": food_review.json()["pageProps"]["outlet"]["uid"],

                        "reviews_rating": {
                            "total_ratings": food_review.json()["pageProps"]["outlet"]["ratings"],
                            "detail_total_rating": [
                                {
                                    "category_rating": self.RATING[rating["id"]],
                                    "score_rating": rating["count"]
                                } for rating in food_review.json()["pageProps"]["cannedOutlet"]
                            ],
                        },

                        "range_prices": self.PRICE[str(food_review.json()["pageProps"]["outlet"]["priceLevel"])],
                        "restaurant_id": food_review.json()["pageProps"]["outlet"]["uid"],
                        "detail_reviews": ""
                    }


                    logger.info(f'city: {self.__city["name"].lower()}')
                    logger.info(f'restaurant: {restaurant["path"].split("/")[-1]}')
                    logger.info(f'link: {header_required["link"]}')
                    logger.info(f'api review: {api_review}')
                    logger.info(f'restaurant name: {header_required["reviews_name"]}')
                    logger.info(f'card : {index}')
                    logger.info(f'total cards : {len(cards)}')
                    print()


                    header_required["tags"].append(self.DOMAIN)
                    self.__get_review(raw_json=header_required)

                except Exception:
                    ic(api_review)
                    self.__char.append(api_review)



    def main(self) -> None:

        response = self.__retry(url=self.API_CITY)

        cities = response.json()
        for city in cities["pageProps"]["contents"][0]["data"]: # Mengambil Kota
            self.__city = city
            response = self.__retry(url=f'https://gofood.co.id/_next/data/8.10.0/id/{self.__city["name"].lower()}/restaurants.json')

            # task_executor = []
            for restaurant in response.json()["pageProps"]["contents"][0]["data"]: # Mengambil restaurant dari kota

                # task_executor.append(self.__executor.submit(self.__extract_restaurant, restaurant))
                self.__extract_restaurant(restaurant)

            # wait(task_executor)
            # self.__executor.shutdown(wait=True)
            self.__file.write_json('private/invalid.json', self.__char)

            break
        ...
