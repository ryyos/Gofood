from zlib import crc32
from time import strftime

class Logs:

    @staticmethod
    def succes(status: str, 
                  total: int, 
                  failed: int, 
                  success: int,
                  source: str,
                  logs_path: str = 'logs/results.txt'
                  ) -> None:
        
        content = {
              "Crawlling_time": strftime('%Y-%m-%d %H:%M:%S'),
              "id_project": crc32('gofood'.encode('utf-8')),
              "id": crc32(source.encode('utf-8')),
              "project":"gofood",
              "source_name": source,
              "total_data": total,
              "total_success": success,
              "total_failed": failed,
              "status": status,
              "assign": 'Rio Dwi Saputra'
            }
        
        with open(logs_path, 'a+', encoding= "utf-8") as file:
            file.write(f'{str(content)}\n')
        ...

    @staticmethod
    def error(status: str, 
                  source: str,
                  message: str,
                  total: int, 
                  failed: int, 
                  success: int,
                  logs_path_err: str = 'logs/detail.txt',
                  logs_path_succ: str = 'logs/results.txt'
                  ) -> None:
        
        detail =   {
                "Crawlling_time": strftime('%Y-%m-%d %H:%M:%S'),
                "id_project": crc32('gofood'.encode('utf-8')),
                "project":"gofood",
                "source_name": source,
                "id": crc32(source.encode('utf-8')),
                "process_name": "Crawling",
                "status": "error",
                "type_error": status,
                "detail_error": message,
                "assign": 'Rio Dwi Saputra'
            }
        
        results = {
              "Crawlling_time": strftime('%Y-%m-%d %H:%M:%S'),
              "id_project": crc32('gofood'.encode('utf-8')),
              "id": crc32(source.encode('utf-8')),
              "project":"gofood",
              "source_name": source,
              "total_data": total,
              "total_success": success,
              "total_failed": failed,
              "status": status,
              "assign": 'Rio Dwi Saputra'
            }

        with open(logs_path_succ, 'a+', encoding= "utf-8") as file:
            file.write(f'{str(results)}\n')

        with open(logs_path_err, 'a+', encoding= "utf-8") as file:
            file.write(f'{str(detail)}\n')