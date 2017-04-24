import operator
from datetime import timedelta, date, datetime
from time import sleep

from functools import reduce


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).hours)):
        yield start_date + timedelta(hours=n)


from django.http import JsonResponse
from django.shortcuts import render
import vk

# ac_tkn
secret_key = "9e68c0209e68c0209e68c020559e33befb99e689e68c020c692502b446e6138e31fb684"


def index(request):
    if request.method == 'POST':

        days_delta = int(request.POST['days'])
        # Дата начала
        start_date = datetime.now() - timedelta(days=days_delta)
        # Конец анализа в сейчас
        end_date = datetime.now()
        # текст поиска
        text = request.POST['text']
        # активируем vk.API
        session = vk.AuthSession('5999290', 'ovdienkoalexandr@mail.ru', '16071607Vk')
        api = vk.API(session)

        temp_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        data = {'likes': [], 'reposts': [], 'comments': [], 'posts': [], }
        # dictf = reduce(lambda x, y: dict((k, v + y[k]) for k, v in x.iteritems()), dict1)

        while temp_date <= end_date:
            '''
                1. Получаем количество записей за день и статистику по первым 1000 записей
                2. Заполняем результирующие массивы с данными
            '''
            posts = []
            # Запрос к API
            start_timestamp = int(temp_date.timestamp())
            end_timestamp = int((temp_date + timedelta(days=1)).timestamp())
            # Скорость запросов к Vk не должна превышать 5/сек
            sleep(0.2)
            response = api.newsfeed.search(q=text,
                                           v="5.63",
                                           count=200,
                                           start_time=start_timestamp,
                                           end_time=end_timestamp)
            posts += response['items']
            total_count = response['total_count']
            # print(response)
            # вытаскиваем данные, пока Vk позволяет
            while response.get('next_form', False):
                # Скорость запросов к Vk не должна превышать 5/сек
                sleep(0.2)
                response = api.newsfeed.search(q=text,
                                               v="5.63",
                                               count=200,
                                               start_time=start_timestamp,
                                               end_time=end_timestamp,
                                               start_form=response['next_form'])
                posts += response['items']

            # заполняем результаты за день
            # дата в UTC измеряется от 00 до 11, а в питоне от 1 до 12, по этму надо сдвинуть месяц
            date_to_highcharts = 'Date.UTC({},{},{})'.format(temp_date.year,temp_date.month-1,temp_date.day)

            data['likes'].append([date_to_highcharts, sum(item['likes']['count'] for item in posts)])
            data['reposts'].append([date_to_highcharts, sum(item['reposts']['count'] for item in posts)])
            data['comments'].append([date_to_highcharts, sum(item['comments']['count'] for item in posts)])
            data['posts'].append([date_to_highcharts, total_count])

            print("Даты",temp_date, start_timestamp, end_timestamp)

            temp_date += timedelta(days=1)
        print(data)

        # ----------------------------------------------

        '''
        print("start date:", int(start_date.timestamp()))
        # текст поиска
        text = request.POST['text']
        # активируем vk.API
        session = vk.Session(access_token=secret_key)
        api = vk.API(session)
        # серия запросов к vk api
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())
        news = []
        total_count = None
        while True:
            # Скорость запросов к Vk не должна превышать 5/сек
            sleep(0.2)
            try:
                response = api.newsfeed.search(q=text,
                                               v="5.63",
                                               count=200,
                                               start_time=start_timestamp,
                                               end_time=end_timestamp)
                if len(response['items']) > 0:
                    news += response['items']
                    # в следующий раз вытягиваем записи начиная с того времени
                    # на котором закончили (последний элемент самый новый)
                    start_timestamp = int(response['items'][-1]['date'])
                    print('start_timestamp:', start_timestamp)
                    if total_count == None:
                        total_count = response['total_count']
                else:
                    break
            except:
                print(response)

        print('Новостей найдено:', len(news))
        # обработка


        # сортируем массив по дням
        days = {}
        #dictf = reduce(lambda x, y: dict((k, v + y[k]) for k, v in x.iteritems()), dict1)
        for item in news:
            date_key = datetime.fromtimestamp(item['date']).strftime('%H-%d-%m-%Y')
            # print(date_key, item['date'])
            stat = [item['likes']['count'], item['reposts']['count'], item['comments']['count'], 1]
            try:
                days[date_key] = [x + y for x, y in zip(days[date_key], stat)]
            except:
                days[date_key] = stat

        data = {'likes': [], 'reposts': [], 'comments': [], 'posts': []}

        if len(news) > 0:
            start_date = datetime.fromtimestamp(news[len(news) - 1]['date'])
            # print(start_date, len(news))
            temp_date = start_date

            while temp_date <= datetime.now():
                date_key = temp_date.strftime('%H-%d-%m-%Y')
                date_to_highcharts = temp_date.strftime('Date.UTC(%Y,%m,%d,%H)')
                # print(date_key)
                try:
                    # print(days[date_key])
                    data['likes'].append([date_to_highcharts, days[date_key][0]])
                    data['reposts'].append([date_to_highcharts, days[date_key][1]])
                    data['comments'].append([date_to_highcharts, days[date_key][2]])
                    data['posts'].append([date_to_highcharts, days[date_key][3]])
                except:
                    data['likes'].append([date_to_highcharts, 0])
                    data['reposts'].append([date_to_highcharts, 0])
                    data['comments'].append([date_to_highcharts, 0])
                    data['posts'].append([date_to_highcharts, 0])
                temp_date += timedelta(hours=1)
        '''
        return render(request, 'Social/index.html',
                      {'posts_count': len(posts), 'data': data, 'text': text, 'total_count': total_count})

    return render(request, 'Social/index.html', {})
