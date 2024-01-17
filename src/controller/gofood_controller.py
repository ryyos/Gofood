import uuid
import os
import imghdr
import requests

from requests.exceptions import MissingSchema
from requests import Response
from fastapi import  File, UploadFile, APIRouter
from fastapi.responses import JSONResponse
from http import HTTPStatus
from pathlib import Path

from src.service.monitor_service import Monitor
from src.model.bodyResponse import BodyResponse

class BingController:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.get('/monitor')(self.__search_image_by_url)

    async def __search_by_source(self, name_source: str) -> JSONResponse:
        try:
            
            name: str = f'{uuid.uuid4()}.{format}'
            path: Path = Path(f'{os.getcwd()}/{name}')

            response: dict = Bing().search_by_image(str(path))

            return JSONResponse(content=BodyResponse(HTTPStatus.OK, data=response).__dict__, status_code=HTTPStatus.OK)
        except Exception as e:
            path.unlink(missing_ok=True)
            return JSONResponse(content=BodyResponse(HTTPStatus.INTERNAL_SERVER_ERROR, message=str(e)).__dict__, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)            

    async def __search_image_by_url(self, url_image: str = None) -> JSONResponse:
        try:
            response: Response = requests.get(url_image, stream=True)
            if(response.status_code != 200): 
                return JSONResponse(content=BodyResponse(HTTPStatus.NOT_FOUND, None, message='url image not found').__dict__, status_code=HTTPStatus.NOT_FOUND)
            
            format: str = imghdr.what(None, b"".join(response.iter_content(chunk_size=128)))

            if(not format): 
                return JSONResponse(content=BodyResponse(HTTPStatus.BAD_REQUEST, None, message='url not contain image').__dict__, status_code=HTTPStatus.BAD_REQUEST)
            response: dict = Bing().search_by_url(url_image)
            return JSONResponse(content=BodyResponse(HTTPStatus.OK, response).__dict__, status_code=HTTPStatus.OK)
        
        except MissingSchema as e:
            return JSONResponse(content=BodyResponse(HTTPStatus.INTERNAL_SERVER_ERROR, message=str(e)).__dict__, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
        except Exception as e:
            return JSONResponse(content=BodyResponse(HTTPStatus.INTERNAL_SERVER_ERROR).__dict__, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

bingController: BingController = BingController()