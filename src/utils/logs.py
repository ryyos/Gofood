from zlib import crc32
from time import strftime

class Logs:

    def succes(self, 
                  status: str, 
                  total: int, 
                  failed: int, 
                  success: int,
                  source: str
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
              "assign": self.PIC
            }
        
        with open(self.LOG_PATH_SUC, 'a+', encoding= "utf-8") as file:
            file.write(f'{str(content)}\n')
        ...

    def error(self,
                  status: str, 
                  source: str,
                  message: str
                  ) -> None:
        
        content =   {
                "Crawlling_time": strftime('%Y-%m-%d %H:%M:%S'),
                "id_project": crc32('gofood'.encode('utf-8')),
                "project":"gofood",
                "source_name": source,
                "id": crc32(source.encode('utf-8')),
                "process_name": "Crawling",
                "status": "error",
                "type_error": status,
                "detail_error": message,
                "assign": self.PIC
            }

        with open(self.LOG_PATH_ERR, 'a+', encoding= "utf-8") as file:
            file.write(f'{str(content)}\n')