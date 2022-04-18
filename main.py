import os

import index
import query


if __name__ == '__main__':
    print("Приветствую вас на поисковике от команды not_yandex")
    print("Для начала выберите, в какой папке проводить поиск")
    print("Если вы хотите проводить поиск во всех папках, введите all")
    searcher = index.SearchIndex()
    get = input()
    if get.lower() == "all":
        directories = os.listdir('files/')
        for directory in directories:
            searcher.add_files('files/' + directory)
        print(f"Директории успешно подключены")
    else:
        while True:
            try:
                files = os.listdir('files/' + get)
                break
            except:
                print("Данная директория не найдена в папке 'files/', попробуйте ещё раз")
                get = input()
        searcher.add_files(f'files/{get}')
        print(f"Директория {'files/' + get} успешно подключена")
        searcher.set_directory(f'files/{get}')
    print("Анализ файлов...")
    searcher._create()
    print("Введите запрос")
    querier = query.QuerySet(searcher)
    demand = input()
    answer = querier.phrase_query(demand)
    if answer:
        print("Файлы, подходящие к вашему запросу:")
    else:
        print("По запросу ничего не найдено.")
    for ans in answer:
        print(ans)
