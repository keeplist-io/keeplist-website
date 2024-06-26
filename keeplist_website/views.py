from django.shortcuts import render
import requests
import json
from .models import *
from django.templatetags.static import static
from django.shortcuts import redirect
from urllib.parse import urlparse

def get_api_url(url_ending):
    return "https://dev.keeplist.io/api/v1/"+url_ending

def splash_page_view(request):
    if request.user_agent.is_mobile or False:
        return render(request, 'a_pages/mobile_splash.html')
    
    return render(request, 'a_pages/splash.html')

def mobile_splash_content_view(request):
    is_iOS = request.user_agent.os.family == "iOS" or False
    
    if is_iOS:
        app_store_url = ""
        app_store_text_image = static("apple-store-text.svg")
        app_store_image = static("apple-icon.svg")
    else:
        app_store_url = ""
        app_store_text_image = static("google-play-text.svg")
        app_store_image = static("google-play-icon.svg")
    
    url = request.META.get("HTTP_REFERER")
    path = urlparse(url).path
    
    match path:
        case "/notifications/":
            splash_image = static("mobile-notifications-screen.png")
        case "/search/":
            splash_image = static("mobile-search-screen.png")
        case "/profile/":
            splash_image = static("mobile-profile-screen.png")
        case _:
            splash_image = static("mobile-home-screen.png")
            
    
    return render(request, 'includes/mobile_splash_content.html', {'splash_image': splash_image, 'app_store_url': app_store_url, 'app_store_image': app_store_image, 'app_store_text_image': app_store_text_image})

def get_menu_items(request):
    items = [
                {   "text": "Home",
                    "url": "/",
                    "icon": static("home.svg"),
                    "icon_selected": static("home-filled.svg"),
                    "is_selected": False
                },
                { "text": "Search",
                    "url": "/search/",
                    "icon": static("search.svg"),
                    "icon_selected": static("search-filled.svg"),
                    "is_selected": False
                },
                { "text": "Notifications",
                    "url": "/notifications/",
                    "icon": static("bell.svg"),
                    "icon_selected": static("bell-filled.svg"),
                    "is_selected": False
                },
                { "text": "Profile",
                    "url": "/profile/",
                    "icon": static("user-circle.svg"),
                    "icon_selected": static("user-circle-filled.svg"),
                    "is_selected": False
                }
            ]
    
    url = request.META.get("HTTP_REFERER")
    path = urlparse(url).path
    #find item where url is equal. then set is selected and icon
    for item in items:
        if item["url"] == path:
            item["icon"] = item["icon_selected"]
            item["is_selected"] = True
    
    return items

def mobile_menu_view(request):
    items = get_menu_items(request)
    
    return render(request, 'includes/mobile_menu.html', {'items': items})

def menu_view(request):
    items = get_menu_items(request)
    
    return render(request, 'includes/menu.html', {'items': items})

def header_content_view(request):
    last_view = request.GET.get('last_view', "")
    last_url = request.GET.get('last_url', "")
    title = request.GET.get('title', "")
    num_links = request.GET.get('num_links', 0)
    user_id = request.GET.get('user_id', "")
    list_id = request.GET.get('list_id', "")
    subtitle = ""
    
    if int(num_links) > 1:
        subtitle = f"{num_links} links"
    elif int(num_links) == 1:
        subtitle = f"{num_links} link"
    
    header_info = {
        "subtitle": subtitle,
        "hx_vals": {}
    }
    
    if last_url:
        header_info["hx_vals"]["last_url"] = last_url
    
    if last_view:
        header_info["hx_vals"]["last_view"] = last_view
    
    if title:
        header_info["hx_vals"]["title"] = title
    
    if user_id:
        header_info["hx_vals"]["user_id"] = user_id
        
    if list_id:
        header_info["hx_vals"]["list_id"] = list_id
    
    return render(request, 'includes/header_content.html', {'header_info': header_info})

def keeplist_preview_view(request):
    user_id = request.GET.get("user_id", "")
    endpoint = get_api_url('lists/?list_type=KP&user='+user_id)
    response = requests.get(endpoint)
    list_data = response.json()
    keeplists = []
    
    for list in list_data['results']:
        if len(list['items']) == 0:
            continue
        
        endpoint = get_api_url('items/?page_size=3')
        endpoint = get_api_url('items/?list='+list["id"]+'&page_size=3')
        response = requests.get(endpoint)
        item_data = response.json()
        
        for item in item_data['results']:
            if not item["imageurl"]:
                item["imageurl"] = "https://images.newscientist.com/wp-content/uploads/2024/05/15214800/SEI_204280908.jpg"
        
        list['items'] = item_data['results']
        keeplists.append(list)
    
    return render(request, 'includes/keeplist_preview_container.html', {'keeplists': keeplists, 'user_id': user_id, 'view':'/profile-view/'+user_id, 'url': "/profile/"+user_id})
    
def bookmarks_preview_view(request):
    user_id = request.GET.get("user_id", "")
    endpoint = get_api_url('lists/?list_type=BK&user='+user_id)
    response = requests.get(endpoint)
    list_data = response.json()
    bookmarks = []
    
    for list in list_data['results']:
        if len(list['items']) == 0:
            continue
        
        endpoint = get_api_url('items/?list='+list["id"]+'&page_size=3')
        response = requests.get(endpoint)
        item_data = response.json()
        
        for item in item_data['results']:
            if not item["imageurl"]:
                item["imageurl"] = "https://images.newscientist.com/wp-content/uploads/2024/05/15214800/SEI_204280908.jpg"
        
        list['items'] = item_data['results']
        bookmarks.append(list)
    
    return render(request, 'includes/bookmarks_preview_container.html', {'bookmarks': bookmarks, 'user_id': user_id, 'view':'/profile-view/'+user_id, 'url': "/profile/"+user_id})

def get_user(user_id):
    endpoint = get_api_url('users/'+user_id)
    response = requests.get(endpoint)
    
    try:
        return response.json()
    except:
        return None

def get_profile_data(session, user_id):
    #sessions aren't working ATM
    session_user_id = session.get("kp_user_id", user_id)
    session_user = session.get("kp_user", get_user(user_id))
    
    if session_user_id != user_id:
        session["kp_user_id"] = user_id
        user = get_user(user_id)
                
        if not user['profile_pic']:
            user['profile_pic'] = "https://images.newscientist.com/wp-content/uploads/2024/05/15214800/SEI_204280908.jpg"
            
        session["kp_user"] = user
        
    #is this needed?
    session.modified = True
    
    #todo : when does session expire?
    return session.get("kp_user", get_user(user_id))

def profile_page_view(request, user_id=""):    
    return render(request, 'a_pages/profile.html', {'user_id': user_id})

def profile_view(request, user_id="", user_name=""):
    if not user_id:
        user_id = request.GET.get("user_id", "")
        
    if not user_name:
        user_name = request.GET.get("user_name", "")

    #if no user name, fetch it
    if not user_name:
        user = get_profile_data(request.session, user_id)
        
        if not user:
            # need this to go to profile page not load the profile splash view within this view
            response = redirect('/')
            return response
            
        user_name = user.get("name", "No Name")
    
    return render(request, 'includes/profile.html', {'user_id': user_id, 'user_name': user_name})

def profile_content_view(request, user_id=""):
    if not user_id:
        user_id = request.GET.get("user_id", "")
        
    user = get_profile_data(request.session, user_id)
    
    return render(request, 'includes/profile_content.html', {'user': user})

def profile_header_view(request, user_id=""):
    if not user_id:
        user_id = request.GET.get("user_id", "")
    
    user = get_profile_data(request.session, user_id)
    #to do: only pass the data props that are needed
    return render(request, 'includes/profile_header.html', {'user': user})

def list_page_view(request, list_id=""):
    endpoint = get_api_url('items/?list='+list_id)
    response = requests.get(endpoint)
    data = response.json()
    
    if (len(data['results']) == 0):
        return render(request, 'a_pages/splash.html')
    
    user_id = data['results'][0]['user']['id']
    list_title = data['results'][0]['list']['title']
    last_url = "/profile/"+user_id
    last_view = "/profile-view/"+user_id
    num_links = len(data["results"])
    
    return render(request, 'a_pages/list.html', {'user_id': user_id, 'list_id': list_id, 'num_links': num_links, 'title': list_title, 'last_url': last_url, 'last_view': last_view, 'view': '/list-view/'+list_id, 'url': "/list/"+list_id})

def list_content_view(request, list_id=""):
    if not list_id:
        list_id = request.GET.get("list_id", "")
    
    endpoint = get_api_url('items/?list='+list_id)
    response = requests.get(endpoint)
    data = response.json()

    if (len(data['results']) == 0):
        return render(request, 'includes/splash_content.html')
    
    for item in data['results']:
            # what default image should be used?
            if not item["imageurl"]:
                item["imageurl"] = "https://images.newscientist.com/wp-content/uploads/2024/05/15214800/SEI_204280908.jpg"
    
    #check for null results, is this the best way to get user and list?
    user_id = data['results'][0]['user']['id']
    list_title = data['results'][0]['list']['title']
    last_view = "/profile-view/"+user_id
    last_url = "/profile/"+user_id
    
    num_links = len(data["results"])
    
    return render(request, 'includes/list_content.html', {'results': data["results"], 'list_id': list_id, 'user_id': user_id, 'num_links': num_links, 'title': list_title, 'last_url': last_url, 'last_view': last_view, 'view': '/list-view/'+list_id, 'url': "/list/"+list_id})

def list_view(request, list_id=""):
    if not list_id:    
        list_id = request.GET.get("list_id", "")
        
    list_name = request.GET.get("list_name", "")
    
    if list_name:
        request.session['list_name'] = list_name
        
    list_name = request.session.get('list_name', '')
    
    if not list_name:
        list_name = "NO NAME!"
        
    user_id = request.GET.get("user_id", "")
    
    #if not list_name:
        #list_name = "To Do"
        
        #endpoint = get_api_url('items/?list='+list_id)
        #response = requests.get(endpoint)
        #data = response.json()
        #user_id = data['results'][0]['user']['id']
        #list_name = data['results'][0]['list']['title']
    
    last_url = ""
    last_view = ""
        
    if user_id:
        last_url = "/profile/"+user_id
        last_view = "/profile-view/"+user_id
        
    #to do
    num_links = 0
    
    return render(request, 'includes/list.html', {'list_id': list_id, 'user_id': user_id, 'title': list_name, 'last_url': last_url, 'last_view': last_view, 'view': '/list-view/'+list_id, 'url': "/list/"+list_id, 'num_links': num_links})

def item_page_view(request, item_id=""):
    endpoint = get_api_url('items/'+item_id)
    response = requests.get(endpoint)
    data = response.json()
    list_id = data['list']['id']
    
    last_url = "/list/"+list_id
    last_view = "/list-view/"+list_id
    
    return render(request, 'a_pages/item.html', {'item_id': item_id, 'list_id': list_id, 'last_url': last_url, 'last_view': last_view})

def item_view(request, item_id="", user_id="", list_id="", last_view="", last_url=""):
    if not item_id:    
        item_id = request.GET.get('item_id', "")
        
    if not list_id:    
        list_id = request.GET.get('list_id', "")
        
    if not user_id:    
        user_id = request.GET.get('user_id', "")
    
    if not last_view:
        last_view = request.GET.get("last_view", "")
        
    if not last_url:
        last_url = request.GET.get("last_url", "")
    
    return render(request, 'includes/item.html', {'user_id': user_id, 'item_id': item_id, 'list_id': list_id, 'last_url': last_url, 'last_view': last_view})

def item_content_view(request):
    item_id = request.GET.get('item_id', "")
    #last_view = request.GET.get("last_view", "")
    #last_url = request.GET.get("last_url", "")
    endpoint = get_api_url('items/'+item_id)
    response = requests.get(endpoint)
    data = response.json()
    
    if not data["imageurl"]:
        data["imageurl"] = "https://images.newscientist.com/wp-content/uploads/2024/05/15214800/SEI_204280908.jpg"
        
    if not data["icon"]:
        data["icon"] = "https://images.newscientist.com/wp-content/uploads/2024/05/15214800/SEI_204280908.jpg"
    
    return render(request, 'includes/item_content.html', {'item': data, 'user_id': data["user"]["id"]})

def more_items_view(request):
    list_id = request.GET.get("list_id")
    item_id = request.GET.get("item_id")
    
    endpoint = get_api_url('items/?list='+list_id)
    response = requests.get(endpoint)
    data = response.json()
    user_name = data['results'][0]["user"]["name"]
    items = []
    
    for item in data['results']:
            if not item["imageurl"]:
                item["imageurl"] = "https://images.newscientist.com/wp-content/uploads/2024/05/15214800/SEI_204280908.jpg"
                
            if item["id"] != item_id:
                items.append(item)
    
    #remove item_id
    
    #check for null results, is this the best way to get user and list?
    #user_id = data['results'][0]['user']['id']
    #list_title = data['results'][0]['list']['title']
    last_view = "/list-view/"+list_id
    last_url = "/list/"+list_id
    
    return render(request, 'includes/more_items.html', {'results': items, 'list_id': list_id, 'user_name': user_name, 'last_url': last_url, 'last_view': last_view})

def item_page(request):
    #url = request.GET['url']
    #iframe = "<iframe src=\"https://cdn.iframe.ly/api/iframe?url=https%3A%2F%2Flichess.org%2F51Br9HIq%2Fblack&key=82dfff236d669d34ba48b5d31cfe2080\" style=\"top: 0; left: 0; width: 100%; height: 100%; position: absolute; border: 0;\" allowfullscreen></iframe>"
    #title = request.GET['title']
    #print(iframe)
    
    #using item_id, get item_details
    item_id = request.GET['item_id']
    endpoint = get_api_url('items/'+item_id)
    response = requests.get(endpoint)
    data = response.json()
    
    return render(request, 'includes/item_page.html', {'item': data})