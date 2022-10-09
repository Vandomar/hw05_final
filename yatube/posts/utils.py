from django.conf import settings
from django.core.paginator import Paginator


def get_paginator(list, request):
    paginator = Paginator(list, settings.AMOUNT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }
