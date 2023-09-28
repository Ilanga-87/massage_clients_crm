months_dict = {
    'January': 'Январь',
    'February': 'Февраль',
    'March': 'Март',
    'April': 'Апрель',
    'May': 'Май',
    'June': 'Июнь',
    'July': 'Июль',
    'August': 'Август',
    'September': 'Сентябрь',
    'October': 'Октябрь',
    'November': 'Ноябрь',
    'December': 'Декабрь'
}

months_list = [month for month in months_dict.values()]


def get_year_dict():
    year_dict = dict()

    for month in months_list:
        year_dict[month] = 0

    return year_dict
