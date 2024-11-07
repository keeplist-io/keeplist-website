from django.templatetags.static import static
from datetime import datetime
from django_htmx.http import HttpResponseClientRedirect
from keeplist_website.api import api, async_render, get_time_label, get_url_path


images_url = "https://images.keeplist.io/"


async def mobile_splash_content_view(request):
    if request.user_agent.os.family == "iOS":
        app_store_url = ""
        app_store_text_image = static("apple-store-text.svg")
        app_store_image = static("apple-icon.svg")
    else:
        app_store_url = ""
        app_store_text_image = static("google-play-text.svg")
        app_store_image = static("google-play-icon.svg")
    
    path = get_url_path(request)
    
    match path:
        # case "/notifications/":
        #     splash_image = static("mobile-notifications-screen.png")
        # case "/search/":
        #     splash_image = static("mobile-search-screen.png")
        # case "/profile/":
        #     splash_image = static("mobile-profile-screen.png")
        case _:
            splash_image = static("mobile-home-screen.png")
            
    
    return await async_render(request, 'includes/mobile_splash_content.html', {'splash_image': splash_image, 'app_store_url': app_store_url, 'app_store_image': app_store_image, 'app_store_text_image': app_store_text_image})

async def get_menu_items(request):
    items = [
                {   "text": "Home",
                    "url": "/",
                    "icon": static("home.svg"),
                    "icon_selected": static("home-filled.svg")
                },
                # {   "text": "Search",
                #     "url": "/search/",
                #     "icon": static("search.svg"),
                #     "icon_selected": static("search-filled.svg")
                # },
                # {   "text": "Notifications",
                #     "url": "/notifications/",
                #     "icon": static("bell.svg"),
                #     "icon_selected": static("bell-filled.svg")
                # },
                # {   "text": "Profile",
                #     "url": "/profile/",
                #     "icon": static("user-circle.svg"),
                #     "icon_selected": static("user-circle-filled.svg")
                # }
            ]
    
    path = await get_url_path(request)
    
    #find item where url is equal. then set is selected and icon
    for item in items:
        item["is_selected"] = False
        if item["url"] == path:
            item["is_selected"] = True
    
    return items

async def mobile_menu_view(request):
    items = await get_menu_items(request)
    
    return await async_render(request, 'includes/mobile_menu.html', {'items': items})

async def menu_view(request):
    items = await get_menu_items(request)
    
    return await async_render(request, 'includes/menu.html', {'items': items})

async def header_content_view(request):
    num_links = request.GET.get('num_links', 0)
    subtitle = ""
    
    if int(num_links) > 1:
        subtitle = f"{num_links} links"
    elif int(num_links) == 1:
        subtitle = f"{num_links} link"
    
    header_info = {
        "subtitle": subtitle,
        "title": request.GET.get('title', ""),
        "hide_bottom_border": request.GET.get("hide_bottom_border", False)
    }
    
    return await async_render(request, 'includes/header_content.html', {'header_info': header_info})

async def keeplist_preview_view(request, user_id):    
    list_data = await api.get_user_lists(user_id, "lists")
    keeplists = list_data.get('results', [])
    
    if not user_id or not list_data or not keeplists:
        return await async_render(request, 'includes/no_content.html', {"range": range(3), "message": "No link items published yet"})

    for kl in keeplists:
        if kl.get('items', None):
            kl['items'] = kl['items'][:3]
    
    return await async_render(request, 'includes/keeplist_preview_container.html', {'keeplists': keeplists, 'user_id': keeplists[0].get('user', {}).get('username')})
    
async def bookmarks_preview_view(request, user_id):
    list_data = await api.get_user_lists(user_id, "keeps", nested=False)
    list_results = list_data.get('results', [])
    
    if not user_id or not list_data or not list_results or len(list_results) == 0:
        return await async_render(request, 'includes/no_content.html', {"range": range(3), "message": "No bookmarks added yet"})

    all_bookmarks = []

    for list in list_results:
        items = list.get('items', [])
        bookmark_items = []
        for item in items:
            if item.get("ref_relation", None):
                item["imageurl"] = item["ref_relation"]["imageurl"]
            if item.get("content", None):
                item["imageurl"] = item["content"][0].get("file", "")
            if len(bookmark_items) < 4:
                bookmark_items.append(item)
            if len(all_bookmarks) < 8:
                all_bookmarks.append(item)
        list['items'] = items
        list['bookmark_items'] = bookmark_items

            

        
    return await async_render(request, 'includes/bookmarks_preview_container.html', {'all_bookmarks': all_bookmarks[:8], 'bookmark_lists': list_results, 'user_id': user_id})


async def bookmarks_view(request, user_id):
    list_results = await api.get_user_lists(user_id, "keeps")    
    
    if not list_results:
        return HttpResponseClientRedirect("/")
    
    bookmark_categories = []
    
    for bk_list in list_results["results"]:
        if bk_list["items"]:
            bookmark_categories.append(bk_list)
    
    return await async_render(request, 'includes/bookmarks.html', {'categories': bookmark_categories, 'user_id': user_id})

async def bookmarks_content_view(request, user_id, list_id=None):
    data = {}
    
    # if no list id, then get all bookmarks
    if not list_id:
        data = await api.get_items(user_id, "keeps")
    else:
        data = await api.get_list_items(user_id, "keeps", list_id)
        
    bookmarks = []
    
    for item in data['results']:
        if item["ref_relation"]:
            item = item["ref_relation"]
        if item.get("content", None):
            item["imageurl"] = item["content"][0].get("file", "")
            
        item["user"]["profile_pic"] = images_url + item["user"]["profile_pic"]
        bookmarks.append(item)    

    return await async_render(request, 'includes/bookmarks_content.html', {'bookmarks': bookmarks, 'list_id': list_id, 'user_id': user_id})

async def share_modal_view(request):
    user_id = request.GET.get("user_id", "")
    profile_url = 'profile/'+user_id
    full_profile_url = 'https://keeplist.io/' + profile_url
    
    if request.user_agent.is_mobile:
        is_iOS = request.user_agent.os.family == "iOS"
    
        if is_iOS:
            app_store_url = ""
            app_store_text_image = static("apple-store-text.svg")
            app_store_image = static("apple-icon.svg")
        else:
            app_store_url = ""
            app_store_text_image = static("google-play-text.svg")
            app_store_image = static("google-play-icon.svg")
            view_path = 'includes/mobile_share_modal.html'
            
        return await async_render(request, 'includes/mobile_share_modal.html', {'profile_url': profile_url, 'app_store_url': app_store_url, 'app_store_image': app_store_image, 'app_store_text_image': app_store_text_image})
        
    return await async_render(request, 'includes/share_modal.html', {'profile_url': profile_url, 'full_profile_url': full_profile_url})


async def profile_view(request, user_id):
    if request.session.get('current_user', {}).get('name', None):
        user = await api.get_user(user_id)
        user_name = user["name"]
    else:
        user_name = request.session.get('current_user', {}).get('name', "")

    return await async_render(request, 'includes/profile.html', {
        'user_id': user_id,
        'user_name': user_name
    })

async def profile_content_view(request, user_id):
    
    user = await api.get_user(user_id)
    lists = await api.get_user_lists(user_id, "keeps")
    
    if not user or user.get("error", {}).get("status_code", "") == 404:
        return HttpResponseClientRedirect("/")
    
    # socials = process_socials(user.get("metadata", {}).get("socials", []))
    
    return await async_render(request, 'includes/profile_content.html', {
        'user': user,
        'lists': lists,
        'socials': []
    })

async def list_content_view(request, user_id, list_type, list_id):
    title = request.GET.get("title", "")
    list_result = await api.get_list_items(user_id, list_type, list_id)
    
    if not list_result:
        return HttpResponseClientRedirect("/")

    if (len(list_result['results']) == 0):
        return HttpResponseClientRedirect("/")
    
    for item in list_result['results']:
        if item.get("content", None):
            item["imageurl"] = item["content"][0]["file"]
    
    num_links = len(list_result["results"])
    
    return await async_render(request, 'includes/list_content.html', {'results': list_result["results"], 'list_id': list_id, 'user_id': user_id, 'list_type': list_type, 'num_links': num_links, 'title': title})

async def list_view(request, user_id, list_type, list_id):
    title = request.GET.get("title", "")
    return await async_render(request, 'includes/list.html', {'list_id': list_id, 'title': title, 'list_type': list_type, 'user_id': user_id})

async def item_view(request, user_id, list_type, list_id, item_id):    
    return await async_render(request, 'includes/item.html', {'user_id': user_id, 'item_id': item_id, 'list_type': list_type, 'list_id': list_id})

async def item_content_view(request, item_id, user_id, list_type, list_id):    
    item_data = await api.get_list_item(user_id, list_type, list_id, item_id)
    
    #this seems like the best way to do this
    if item_data.get("ref_relation", None):
        item_data = item_data["ref_relation"]
        
    item_data["user"]["profile_pic"] = images_url + item_data["user"]["profile_pic"]
    
    if item_data.get("content", None):
        item_data["imageurl"] = item_data["content"][0].get("file", "")
    title = item_data.get("list", {}).get("title", "")
    created = datetime.now() - datetime.strptime(item_data["created"], '%Y-%m-%dT%H:%M:%S.%fZ')
    created_label = await get_time_label(created)
    return await async_render(request, 'includes/item_content.html', {'item': item_data, 'user': item_data["user"], 'created': created_label, 'list_id': list_id, 'title': title})

async def more_items_view(request, user_id, list_type, item_id=None):
    if not item_id:
        item_id = request.GET.get("item_id", "")
    
    if request.session.get('current_user', {}).get('name', None):
        user = await api.get_user(user_id)
        user_name = user["name"]
    else:
        user_name = request.session.get('current_user', {}).get('name', "")
    

    
    data = await api.get_items(user_id, list_type)
    items = []
    
    import random
    
    for item in data['results']:
        if item["ref_relation"]:
            item = item["ref_relation"]            
        
        if item["id"] != item_id:
            if item.get("content", None):
                item["imageurl"] = item["content"][0].get("file", "")
            items.append(item)
    
    random.shuffle(items)
    return await async_render(request, 'includes/more_items.html', {'items': items[:6], 'user_id': user_id, 'user_name': user_name, 'list_type': list_type})


### Seems like this is no longer used
# async def item_page(request):    
#     item_id = request.GET.get('item_id', "")
#     user_id = request.GET.get('user_id', "")
#     list_type = request.GET.get('list_type', "")
#     list_id = request.GET.get('list_id', "")
    
#     data = await api.get_list_item(user_id, list_type, list_id, item_id)
    
#     return await async_render(request, 'includes/item_page.html', {'item': data})

