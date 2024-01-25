import os
import json

from zlib import crc32
from time import strftime

class Logs:

    @staticmethod
    def read(path: str):
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
        ...

    @staticmethod
    def write(path: str, content: any):
        with open(path, 'w', encoding="utf-8") as file:
            json.dump(content, file, ensure_ascii=False, indent=2, default=str)
        ...

    @staticmethod
    def runtime(total: int, 
                failed: int, 
                success: int,
                uid: str,
                sub_source: str,
                id_data: int,
                status_runtime: str,
                status_conditions: str,
                type_error: str,
                message: str
                ) -> None:

        MONITORING_DATA = 'logs/monitoring_gofood.json'
        MONITORING_LOG = 'logs/monitoring_logs.json'

        content = {
            "Crawlling_time": strftime('%Y-%m-%d %H:%M:%S'),
            "id_project": None,
            "project": "Data Intelligence",
            "sub_project": "data review",
            "source_name": "gofood.co.id",
            "sub_source_name": sub_source,
            "id_sub_source": uid,
            "total_data": total,
            "total_success": success,
            "total_failed": failed,
            "status": status_conditions,
            "assign": "Rio"
        }

        monitoring = {
            "Crawlling_time": strftime('%Y-%m-%d %H:%M:%S'),
            "id_project": None,
            "project": "Data Intelligence",
            "sub_project": "data review",
            "source_name": "gofood.co.id",
            "sub_source_name": sub_source,
            "id_sub_source": uid,
            "id_data": id_data,
            "process_name": "Crawling",
            "status": status_runtime,
            "type_error": type_error,
            "message": message,
            "assign": "Rio"
        }


        if not os.path.exists(MONITORING_DATA):
            Logs.write(MONITORING_DATA, [content])
            Logs.write(MONITORING_LOG, [monitoring])



        datas = Logs.read(MONITORING_DATA)
        monitorings = Logs.read(MONITORING_LOG)

        if not datas:
            Logs.write(MONITORING_DATA, [content])
            Logs.write(MONITORING_LOG, [monitoring])

        monitorings.append(monitoring)

        uid_found = False

        for index, data in enumerate(datas):
            if uid in data["id_sub_source"]:
                datas[index]["total_data"] = total
                datas[index]["total_success"] = success
                datas[index]["total_failed"] = failed
                datas[index]["status"] = status_conditions
                uid_found = True
                break

        if not uid_found:
            datas.append(content)

        Logs.write(MONITORING_DATA, datas)
        Logs.write(MONITORING_LOG, monitorings)
        ...
