from zlib import crc32
from time import strftime

class Logs:

    @staticmethod
    def succes(status: str, 
                  total: int, 
                  failed: int, 
                  success: int,
                  uid: str,
                  source: str,
                  logs_path: str = 'logs/logs_gofood.txt'
                  ) -> None:
        
        content = {
              "Crawlling_time": strftime('%Y-%m-%d %H:%M:%S'),
              "id_project": 'Data Intelligence',
              "id": uid,
              "project":"data review",
              "source_name": source,
              "total_data": total,
              "total_success": success,
              "total_failed": failed,
              "status": status,
              "assign": 'Rio'
            }
        
        with open(logs_path, 'a+', encoding= "utf-8") as file:
            file.write(f'{str(content)}\n')
        ...

    @staticmethod
    def error(status: str, 
                  source: str,
                  message: str,
                  total: int, 
                  uid: str,
                  failed: int, 
                  success: int,
                  logs_path_err: str = 'logs/logs_detail.txt',
                  logs_path_succ: str = 'logs/logs_gofood.txt'
                  ) -> None:
        
        detail =   {
                "Crawlling_time": strftime('%Y-%m-%d %H:%M:%S'),
                "id_project": "Data Intelligence",
                "project":"data review",
                "source_name": source,
                "id": uid,
                "process_name": "Crawling",
                "status": "error",
                "type_error": status,
                "detail_error": message,
                "assign": 'Rio'
            }
        
        results = {
              "Crawlling_time": strftime('%Y-%m-%d %H:%M:%S'),
              "id_project": "Data Intelligence",
              "id": uid,
              "project":"data review",
              "source_name": source,
              "total_data": total,
              "total_success": success,
              "total_failed": failed,
              "status": status,
              "assign": 'Rio'
            }

        with open(logs_path_succ, 'a+', encoding= "utf-8") as file:
            file.write(f'{str(results)}\n')

        with open(logs_path_err, 'a+', encoding= "utf-8") as file:
            file.write(f'{str(detail)}\n')