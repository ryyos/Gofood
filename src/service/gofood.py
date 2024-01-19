import os
import datetime as date
import requests
import json

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
        self.__executor = ThreadPoolExecutor()
        self.__city_executor = ThreadPoolExecutor(max_workers=5)

        self.__char: str = []

        self.VERSION = '8.10.2'

        self.DOMAIN = 'gofood.co.id'
        self.MAIN_URL = 'https://gofood.co.id'
        self.MAIN_PATH = 'data'
        self.LOG_PATH = 'logs/logs.txt'
        self.PIC = 'Rio Dwi Saputra'

        self.API_CITY = f'https://gofood.co.id/_next/data/{self.VERSION}/id/cities.json' # 89
        self.RESTAURANT = f'https://gofood.co.id/_next/data/{self.VERSION}/id/jakarta/restaurants.json' # 94
        self.NEAR_ME_API = f'https://gofood.co.id/_next/data/{self.VERSION}/id/jakarta/bekasi-restaurants/near_me.json' 
        self.FOODS_API = f'https://gofood.co.id/api/outlets'
        self.API_REVIEW = f'https://gofood.co.id/_next/data/{self.VERSION}/id/jakarta/restaurant/mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8/reviews.json?id=mcdonald-s-pekayon-50150204-8f6d-4372-8458-668f1be126e8'
        self.API_REVIEW_PAGE = 'https://gofood.co.id/api/outlets/'

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

        self.RESPONSE_CODE = [200, 400, 404, 500]
        ...

    def __logging(self, 
                  url: str, 
                  total: int, 
                  failed: int, 
                  success: int,
                  name_error: str,
                  message: str) -> None:
        
        content = {
              "source": url,
              "total_data": total,
              "total_data_berhasil_diproses": success,
              "total_data_gagal_diproses": failed,
              "PIC": self.PIC,
              "name_error": name_error,
              "message": message
            }
        
        with open(self.LOG_PATH, 'a+', encoding= "utf-8") as file:
            file.write(f'{str(content)}\n')
        ...

    def __convert_time(self, times: str) -> int:
        dt = date.datetime.fromisoformat(times)
        dt = dt.replace(tzinfo=timezone.utc) 

        return int(dt.timestamp())
        ...

    def __retry(self, url: str, 
                action: str = 'get', 
                payload: dict = None, 
                retry_interval: int = 1,
                ):


        match action:

            case 'get':
                retry = 0
                while True:
                    try:
                        response = requests.get(url=url, headers={"User-Agent": self.__faker.random})


                        logger.info(f'user agent: {self.__faker.random}')
                        logger.info(f'response status: {response.status_code}')
                        logger.info(f'try request in url: {url}')
                        logger.info(f'request action: {action}')
                        print()

                        if response.status_code in self.RESPONSE_CODE: return response
                        if response.status_code == 403:
                            ic(response.text)
                            self.__sessions.get(url=self.MAIN_URL, headers={"User-Agent": self.__faker.random})


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
                        print()

                        if response.status_code in self.RESPONSE_CODE: return response
                        if response.status_code == 403: 
                            ic(response.text)
                            self.__sessions.get(url=self.MAIN_URL, headers={"User-Agent": self.__faker.random})

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
                for _ in range(5):
                    try:
                        response = self.__sessions.get(url=url, headers={"User-Agent": self.__faker.random})

                        logger.info(f'response status: {response.status_code}')
                        logger.info(f'try request in url: {url}')
                        logger.info(f'request action: {action}')
                        print()

                        if response.status_code in self.RESPONSE_CODE: return response
                        if response.status_code == 403: 
                            ic(response.text)
                            self.__sessions.get(url=self.MAIN_URL, headers={"User-Agent": self.__faker.random})

                        logger.warning(f'retry interval: {retry_interval}')
                        logger.warning(f'retry to: {retry}')
                        logger.warning(f'response status: {response}')

                        sleep(retry_interval)
                        retry_interval+=5
                        retry+=1

                    except Exception as err:
                        logger.error(err)
                        logger.warning(f'retry interval: {retry_interval}')
                        logger.warning(f'retry to: {retry}')
                        logger.warning(f'response status: {response}')
                        retry+=1

                        sleep(retry_interval)
                        retry_interval+=5

                return False

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
            "pageSize": 50,
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

    def __convert_card(self, card_path: str) -> str:
        ic(card_path)
        if ' ' in card_path: return "/".join(card_path.split("/")[1].split(" ")[0])
        else: return card_path

    def __get_review(self, raw_json: dict):
        logger.info('extract review from restaurant')
        uid = raw_json["restaurant_id"]

        page = '?page=1&page_size=50'
        
        response = self.__retry(url=f'{self.API_REVIEW_PAGE}{uid}/reviews{page}',action='review')

        ...
        all_reviews = []
        if response.status_code == 200:
            page_review = 0
            while True:

                reviews = response.json()["data"]
                for review in reviews: all_reviews.append(review)

                logger.info(f'page review: {page_review}')
                logger.info(f'api review page: {self.API_REVIEW_PAGE}{uid}/reviews{page}')
                print()

                page = response.json().get("next_page", None)
                if page:
                    response = self.__retry(url=f'{self.API_REVIEW_PAGE}{uid}/reviews{page}', action='review')

                    ...
                    if response.status_code != 200: 
                        self.__logging(url=raw_json["link"],
                                       total=len(all_reviews) + int(page.split('=')[-1]),
                                       success=len(all_reviews),
                                       failed=int(page.split('=')[-1]),
                                       name_error=response,
                                       message=response.text)
                        break

                    ...
                    page_review+=1

                else: 
                    logger.warning(f'review finished')
                    self.__logging(url=raw_json["link"],
                                   total=len(all_reviews),
                                   success=len(all_reviews),
                                   failed=0,
                                   name_error=None,
                                   message='success')
                    break

        else:
            self.__logging(url=raw_json["link"],
                           total=int(page.split('=')[-1]),
                           success=len(all_reviews),
                           failed=int(page.split('=')[-1]),
                           name_error=response,
                           message=response.text)

        
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

    def __fetch_card_restaurant(self, restaurant: str) -> List[str]:

        response = self.__retry(url=f'https://gofood.co.id/_next/data/{self.VERSION}/id{restaurant}/near_me.json?service_area={restaurant.split("/")[1]}&locality={restaurant.split("/")[-1]}&category=near_me')
            
        logger.info('fetch card food')


        latitude = response.json()["pageProps"]["userLocation"]["chosenLocation"]["latitude"]
        longitude = response.json()["pageProps"]["userLocation"]["chosenLocation"]["longitude"]

        page_token = 1
        cards = [card["path"] for card in response.json()["pageProps"]["outlets"]] # "/manado/restaurant/martabak-mas-narto-indomaret-a906c98d-2d31-48bc-8408-82dc1350cdca"
        while True:

            response = self.__retry(url=self.FOODS_API, 
                                    action='post',
                                    payload=self.__buld_payload(page=page_token, 
                                                              latitude=latitude,
                                                              longitude=longitude
                                                              ))

            if response.status_code != 200: break


            """ __create_card()

            Param:
                city   = | restaurant (/ketapang/restaurants) -> split("/")[1] -> ketapang
                pieces = | key "tenants/gofood/outlets/816ed6cd-72bf-4e10-9e50-37ce4d83e016" & displayName "Pempek Bang Awie, Wenang"

            Return:
                str: /ketapang/restaurant/pempek-bang-awie-wenang-a906c98d-2d31-48bc-8408-82dc1350cdca
            
            """
            card = [self.__create_card(city=restaurant.split("/")[1], pieces=card) for card in response.json()["outlets"]]
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

    def __extract_restaurant(self, ingredient: dict):
            cards = self.__fetch_card_restaurant(city=ingredient["city"]["name"].lower(), restaurant=ingredient["restaurant"]["path"]) # Mengambil card makanan dari restaurant

            for index, card in enumerate(cards):
                ic(card)

                api_review = f'https://gofood.co.id/_next/data/{self.VERSION}/id{self.__convert_card(card)}/reviews.json?id={card.split("/")[-1]}'
                
                try: 
                    # self.__url_food_review = api_review.replace('--', '-')
                    
                    food_review = self.__retry(api_review.replace('--', '-').replace('--', '-'))
                    logger.info(card)

                    if food_review.json()["pageProps"].get("__N_REDIRECT", None):
                        ic('masuk redirect')
                        ic(food_review.json()["pageProps"]["__N_REDIRECT"])
                        food_review = self.__retry(f'https://gofood.co.id/_next/data/{self.VERSION}/id{food_review.json()["pageProps"]["__N_REDIRECT"]}/reviews.json?id={card.split("/")[-1]}')

                    header_required = {
                        "link": self.MAIN_URL+food_review.json()["pageProps"].get("outletUrl"),
                        "domain": self.DOMAIN,
                        "tags": [tag["displayName"] for tag in food_review.json()["pageProps"]["outlet"]["core"]["tags"]],
                        "crawling_time": strftime('%Y-%m-%d %H:%M:%S'),
                        "crawling_time_epoch": int(time()),
                        "path_data_raw": "",
                        "path_data_clean": "",
                        "reviews_name": food_review.json()["pageProps"]["outlet"]["core"]["displayName"],
                        "location_review": ingredient["city"]["name"].lower(),
                        "category_reviews": "food & baverage",
                        "total_reviews": 0,

                        "location_restaurant": {
                            "city": ingredient["city"]["name"].lower(),
                            "area": ingredient["restaurant"]["path"].split("/")[-1],
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


                    logger.info(f'city: {ingredient["city"]["name"].lower()}')
                    logger.info(f'restaurant: {ingredient["restaurant"]["path"].split("/")[-1]}')
                    logger.info(f'link: {header_required["link"]}')
                    logger.info(f'api review: {api_review}')
                    logger.info(f'restaurant name: {header_required["reviews_name"]}')
                    logger.info(f'card : {index}')
                    logger.info(f'total cards : {len(cards)}')
                    print()


                    header_required["tags"].append(self.DOMAIN)
                    self.__get_review(raw_json=header_required)

                except Exception as err:

                    ic({
                        "error": err,
                        "api_review": api_review,
                        "card": card
                    })
                    
                    self.__char.append(api_review)

    def __extract_city(self, city) -> None:
        response = self.__retry(url=f'https://gofood.co.id/_next/data/{self.VERSION}/id/{city["name"].lower()}/restaurants.json')

        task_executor = []
        for restaurant in response.json()["pageProps"]["contents"][0]["data"]: # Mengambil restaurant dari kota

            ingredient = {
                "restaurant": restaurant,
                "city": city
            }

            # self.__extract_restaurant(restaurant)
            task_executor.append(self.__executor.submit(self.__extract_restaurant, ingredient))

        wait(task_executor)


    def main(self) -> None:

        response = self.__retry(url=self.API_CITY)

        cities = response.json()

        ic(cities)

        task_city_executor = []
        # for city in cities["pageProps"]["contents"][0]["data"]: # Mengambil Kota
        #     task_city_executor.append(self.__city_executor.submit(self.__extract_city, city))

        # wait(task_city_executor)


        ...
