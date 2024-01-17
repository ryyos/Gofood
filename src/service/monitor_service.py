import json

from icecream import ic

class Monitor:

    @staticmethod
    def search_by_source(source: str):
        with open('D:/programming/Python/project/Gofood/logs/logs.txt', 'r', encoding='utf-8') as file:
            datas = json.load(file)

        for data in datas:
            if str(list(data.keys())[0]).lower() == source.replace(' ', '_').lower():
                return data
        ...

    @staticmethod
    def search_with_paging(page: int, limit: int):
        with open('D:/programming/Python/project/Gofood/logs/logs.txt', 'r', encoding='utf-8') as file:
            datas = json.load(file)

        start = (page - 1) * limit
        end = page * limit

        results = [datas[paging] for paging in range(start, end)]
        return results
        ...

    @staticmethod
    def all():
        with open('D:/programming/Python/project/Gofood/logs/logs.txt', 'r', encoding='utf-8') as file:
            datas = json.load(file)

        return datas
        ...

    @staticmethod
    def conclusion():
        with open('D:/programming/Python/project/Gofood/logs/logs.txt', 'r', encoding='utf-8') as file:
            datas = json.load(file)

        total = 0
        failed = 0
        succes = 0
        for data in datas:
            total += data[str(list(data.keys())[0])]["total_data"]
            succes += data[str(list(data.keys())[0])]["total_data_berhasil_diproses"]
            failed += data[str(list(data.keys())[0])]["total_data_gagal_diproses"]

        return {
            "total_data": total,
            "total_data_berhasil_diproses": succes,
            "total_data_gagal_diproses": failed
        }


if __name__ == '__main__':
    ic(Monitor.search_by_source(source='Bobs_Salad_Perum_Kemang_Pratama'))
    ic(Monitor.search_with_paging(page=1, limit=2))
    ic(Monitor.conclusion())