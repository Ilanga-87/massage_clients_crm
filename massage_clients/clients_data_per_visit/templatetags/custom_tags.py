from django import template

register = template.Library()


@register.filter
def get_value(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_client_name(timetable_cell):
    visit = timetable_cell.visit
    return visit.client.name if visit else ''


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
