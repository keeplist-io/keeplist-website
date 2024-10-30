from datetime import datetime
from keeplist_website.api import async_render, api
from django_htmx.http import HttpResponseClientRedirect


async def splash_page_view(request):
    if request.user_agent.is_mobile:
        return await async_render(request, "a_pages/mobile_splash.html")

    return await async_render(request, "a_pages/splash.html")


async def profile_page_view(request, user_id=""):
    if user_id is None:
        return HttpResponseClientRedirect("/")
    user = await api.get_user(user_id)
    request.session["current_user"] = {
        "name": user.get("name"),
        "id": user.get("id"),
        "username": user.get("username"),
        "user": user,
        "last_accessed": datetime.now().isoformat(),
    }
    response = await async_render(
        request, "a_pages/profile.html", {"user_id": user.get("username")}
    )
    return response


async def bookmarks_page_view(request, user_id="", list_id=""):
    if not user_id:
        return await async_render(request, "a_pages/splash.html")

    return await async_render(request, "a_pages/bookmarks.html", {"user_id": user_id})


async def list_page_view(request, user_id="", list_id=""):
    if not list_id or not user_id:
        return await async_render(request, "a_pages/splash.html")
    response = await api.get_list(user_id, "lists", list_id, nested=False)
    if not response:
        return HttpResponseClientRedirect("/")
    items = response.get("items", [])
    if not items:
        return await async_render(request, "a_pages/splash.html")
    title = response.get("title")
    num_links = len(items)
    return await async_render(
        request,
        "a_pages/list.html",
        {
            "user_id": user_id,
            "list_id": list_id,
            "num_links": num_links,
            "title": title,
            "list_type": "lists",
        },
    )


async def item_page_view(request, user_id="", list_type="", list_id="", item_id=""):
    if not item_id or not user_id or not list_type or not list_id:
        return await async_render(request, "a_pages/splash.html")

    item_result = await api.get_list_item(user_id, list_type, list_id, item_id)

    if not item_result:
        return HttpResponseClientRedirect("/")

    if item_result["ref_relation"]:
        item_result = item_result["ref_relation"]

    user_name = item_result["user"]["name"]

    return await async_render(
        request,
        "a_pages/item.html",
        {
            "item_id": item_id,
            "list_id": list_id,
            "user_id": user_id,
            "list_type": list_type,
            "title": item_result.get("list", {}).get("title", ""),
            "user_name": user_name,
        },
    )
