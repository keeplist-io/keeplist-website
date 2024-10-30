import asyncio
import math
from urllib.parse import urlparse
from django_htmx.http import HttpResponseClientRedirect

from django.shortcuts import render
from a_core.api import KeeplistAPI
from asgiref.sync import sync_to_async

api = KeeplistAPI()

async def async_render(request, template, context=None):
    context = context or {}
    response = await sync_to_async(render)(request, template, context)
    if hasattr(response, 'render') and asyncio.iscoroutinefunction(response.render):
        response = await response.render()
    # print('async_render', response.content.decode('utf-8'))
    return response

async def view_404(request, exception=None, name=''):
    return HttpResponseClientRedirect('/')

async def get_url_path(request):
    url = request.META.get("HTTP_REFERER")
    return urlparse(url).path

import asyncio

async def prefetch_related_data(user_id):
    """
    Pre-warm cache with related data likely to be needed
    """
    tasks = [
        api.get_user(user_id),
        api.get_user_lists(user_id, "keeps"),
        api.get_user_lists(user_id, "lists"),
    ]

    return await asyncio.gather(*tasks)



async def get_time_label(dt):
    total_seconds = dt.total_seconds()
    minutes = math.ceil(total_seconds / 60)
    
    if minutes < 2:
        return "now"
    
    if minutes < 60:
        return f"{minutes}min"
    
    hours = math.ceil(minutes / 60)
    
    if hours < 24:
        return f"{hours}h"
    
    days = math.ceil(hours / 24)
    
    if days < 365:
        return f"{days}d"

    years = math.floor(days / 365)
    return f"{years}y"
