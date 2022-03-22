from django.shortcuts import render
import re
import json
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def search(request):
    flag_all = False
    try:
        if request.method == 'GET':
            text = request.GET.get('text')
            pattern_type = request.GET.get('type')
        elif request.method == 'POST':
            text = request.POST.get('text')
            pattern_type = request.POST.get('type')
    except BaseException:
        return HttpResponseBadRequest
    if pattern_type == '0':
        flag_all = True
    result = []
    search_result = pattern_dict[pattern_type].finditer(text)
    for obj in search_result:
        prev_word = pattern_prev_word.search(text, 0, obj.start())
        next_word = pattern_next_word.search(text, obj.end())
        context = prev_word.group() + obj.group() + next_word.group()
        if flag_all:
            pattern_type = index_dict[[name for name, value in obj.groupdict().items() if value is not None][0]]
        obj_info = {'type': pattern_type,
                    'object': obj.group(),
                    'context': context
                    }
        if obj_info not in result:
            result.append(obj_info)
    return HttpResponse(json.dumps(result, ensure_ascii=False))


pattern_domain = r'(?P<domain>(\S+://)?[A-Za-z0-9._%+-]+\.[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}?)'
pattern_phone = r'(?P<phone>((8|\+7)[\- ]?\d{3}[- ])?\d{3}[- ]?[- ]?\d{2}[- ]?\d{2})'
pattern_address = r'(?P<address>((г\W+|д\W+|п\W+)[А-Яа-я\-]+)(\W+(пр\W+|ул\W+|пер\W+)[А-Яа-я\-]+?)(\W+д\W+\d+)(\W+корп\W+\d+)?(\W+кв\W+\d+)?)'
pattern_email = r'(?P<email>[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}?)'
pattern_name = r'(?P<name>[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)'
pattern_prev_word = re.compile(r'(\S+\W+)?$')
pattern_next_word = re.compile(r'(\W+\S+)?')
index_dict = {'domain': '01',
              'phone': '02',
              'address': '03',
              'email': '04',
              'name': '05'
              }
pattern_dict = {'01': re.compile(pattern_domain),
                '02': re.compile(pattern_phone),
                '03': re.compile(pattern_address),
                '04': re.compile(pattern_email),
                '05': re.compile(pattern_name)
                }
pattern_all = '|'.join(value.pattern for value in pattern_dict.values())
pattern_dict['0'] = re.compile(pattern_all)
