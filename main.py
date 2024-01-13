import os
from time import perf_counter

from src import Gofood
from src import logger


if __name__ == '__main__':
    start = perf_counter()
    if not os.path.exists('data'): os.mkdir('data')

    logger.info('Scraping start..')
    go = Gofood()
    go.main()

    logger.info(f'scraping finish: {perf_counter() - start}')