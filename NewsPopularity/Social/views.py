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
        # используется метод POST, анализируем данные

        ''' анализ данных '''
        # количество дней для анализа
        days_delta = int(request.POST['days'])
        # Дата начала
        start_date = datetime.now() - timedelta(days=days_delta)
        # Конец анализа наступает в данный момент
        end_date = datetime.now()
        # текст поиска
        text = request.POST['text']
        # активируем vk.API
        session = vk.AuthSession('6012368', '+79381484469', 'DonNu123')
        api = vk.API(session)
        # в начальной дате отбрасываются часы, минуты. . .
        temp_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        # создание обьекта для последующего заполнения и передачи его в шаблон
        data = {'likes': [], 'reposts': [], 'comments': [], 'posts': [], }
        # dictf = reduce(lambda x, y: dict((k, v + y[k]) for k, v in x.iteritems()), dict1)

        while temp_date <= end_date:
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
            date_to_highcharts = 'Date.UTC({},{},{})'.format(temp_date.year, temp_date.month - 1, temp_date.day)

            data['likes'].append([date_to_highcharts, sum(item['likes']['count'] for item in posts)])
            data['reposts'].append([date_to_highcharts, sum(item['reposts']['count'] for item in posts)])
            data['comments'].append([date_to_highcharts, sum(item['comments']['count'] for item in posts)])
            data['posts'].append([date_to_highcharts, total_count])

            print("Даты", temp_date, start_timestamp, end_timestamp)

            temp_date += timedelta(days=1)

        return render(request, 'Social/index.html',
                      {'data': data,
                       'text': text,
                       'total_count': total_count})

    # используется метод GET, возвращаем пустой шаблон
    return render(request, 'Social/index.html', {})
