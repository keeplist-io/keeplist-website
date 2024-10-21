from django.shortcuts import render
import requests
import json
import math
from .models import *
from django.templatetags.static import static
from django.shortcuts import redirect
from urllib.parse import urlparse
from datetime import datetime
from django_htmx.http import HttpResponseClientRedirect

images_url = "https://images.keeplist.io/"

def view_404(request, exception=None):
    return redirect('/')

def get_api_results(url_ending):
    response = requests.get("https://dev.keeplist.io/api/v1/"+url_ending)
    
    try:
        return response.json()
    except:
        return {}

def get_url_path(request):
    url = request.META.get("HTTP_REFERER")
    return urlparse(url).path

def get_user(user_id):
    return get_api_results('users/'+user_id)

def get_profile_data(session, user_id, call_db=False):
    session_user_id = session.get("kp_user_id", user_id)
    
    if session_user_id != user_id:
        session["kp_user_id"] = user_id
        
        if call_db:
            user = get_user(user_id)
                    
            if not user['profile_pic']:
                #todo: default pic
                user['profile_pic'] = "https://images.newscientist.com/wp-content/uploads/2024/05/15214800/SEI_204280908.jpg"
                
            session["kp_user"] = user
        
    #is this needed?
    session.modified = True
    
    #todo : when does session expire?
    if call_db:
        return session.get("kp_user", get_user(user_id))

    return session.get("kp_user", {})

def clear_history(request):
    request.session["history"] = []
    request.session.modified = True
    
def add_to_history(request, url):
    request.session["history"] = request.session.get("history", [])
    request.session["history"].append(url)
    request.session.modified = True
    
def last_view(request):
    #TODO: there seems to be a race condition. sometimes going back doesn't load the correct item if you click things quickly
    history = request.session.get("history", [])
    
    if history:
        last_view = history.pop()
        
        if history:
            last_view = history.pop()
            
        request.session.modified = True

        return redirect(last_view)

    #TODO: where to redirect?
    return render(request, 'includes/profile.html', {'user_id': "default", 'user_name': "Default"})

def splash_page_view(request):
    if request.user_agent.is_mobile:
        return render(request, 'a_pages/mobile_splash.html')
    
    return render(request, 'a_pages/splash.html')

def mobile_splash_content_view(request):
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
                    "icon_selected": static("home-filled.svg")
                },
                {   "text": "Search",
                    "url": "/search/",
                    "icon": static("search.svg"),
                    "icon_selected": static("search-filled.svg")
                },
                {   "text": "Notifications",
                    "url": "/notifications/",
                    "icon": static("bell.svg"),
                    "icon_selected": static("bell-filled.svg")
                },
                {   "text": "Profile",
                    "url": "/profile/",
                    "icon": static("user-circle.svg"),
                    "icon_selected": static("user-circle-filled.svg")
                }
            ]
    
    path = get_url_path(request)
    
    #find item where url is equal. then set is selected and icon
    for item in items:
        if item["url"] == path:
            item["is_selected"] = True
    
    return items

def mobile_menu_view(request):
    items = get_menu_items(request)
    
    return render(request, 'includes/mobile_menu.html', {'items': items})

def menu_view(request):
    items = get_menu_items(request)
    
    return render(request, 'includes/menu.html', {'items': items})

def header_content_view(request):
    num_links = request.GET.get('num_links', 0)
    history = request.session.get("history", [])
    last_url = ""
    subtitle = ""
    
    if len(history) > 1:
        last_url = history[-2].replace("-view", "", 1) # e.g. turns /profile-view/user_123 into /profile/user_123
    
    if int(num_links) > 1:
        subtitle = f"{num_links} links"
    elif int(num_links) == 1:
        subtitle = f"{num_links} link"
    
    header_info = {
        "subtitle": subtitle,
        "last_url": last_url,
        "title": request.GET.get('title', ""),
        "has_history": len(history) > 1,
        "hide_bottom_border": request.GET.get("hide_bottom_border", False)
    }
    
    return render(request, 'includes/header_content.html', {'header_info': header_info})

def keeplist_preview_view(request):    
    user_id = request.GET.get("user_id", "")
    list_data = get_api_results('lists/?list_type=KP&user='+user_id)
    list_results = list_data['results']
    
    if not user_id or not list_data or not list_results or len(list_results) == 0:
        return render(request, 'includes/no_content.html', {"range": range(3), "message": "No link items published yet"})
    
    keeplists = []
    
    for list in list_results:
        keeplists.append({'id': list['id'], 'title': list['title'], 'items': []})

    item_data = get_api_results('items/?list_type=KP&user='+user_id)
    items = []
    
    for item in item_data['results']:
        current_list_id = item.get('list', {}).get('id', None)
        
        if not current_list_id:
            continue
    
        for list in keeplists:            
            if list['id'] == current_list_id and len(list.get('items', [])) < 3:
                # some items have images under imageurl, others under content.file. why?
                if not item["imageurl"] and item["content"]:
                    item["imageurl"] = item["content"][0].get("file", "")
                    
                list['items'].append(item)
                break
    
    return render(request, 'includes/keeplist_preview_container.html', {'keeplists': keeplists, 'user_id': user_id})
    
def bookmarks_preview_view(request):
    user_id = request.GET.get("user_id", "")    
    list_data = get_api_results('lists/?list_type=BK&user='+user_id)
    list_results = list_data.get('results', [])
    bookmark_lists = []
    
    if not user_id or not list_data or not list_results or len(list_results) == 0:
        return render(request, 'includes/no_content.html', {"range": range(3), "message": "No bookmarks added yet"})
    
    for list in list_results:
        #create list to add bookmarks to
        list['bookmark_items'] = []
        bookmark_lists.append(list)
    
    items = get_api_results('items/?list_type=BK&user='+user_id)
    all_bookmarks = items['results']
    
    for item in all_bookmarks:
        if not item["imageurl"] and item["ref_relation"]:
            item["imageurl"] = item["ref_relation"]["imageurl"]
            
        for list in bookmark_lists:
            if item['list'] and list['id'] == item['list']['id'] and len(list['bookmark_items']) < 4:
                list['bookmark_items'].append(item)
                break
        
    return render(request, 'includes/bookmarks_preview_container.html', {'all_bookmarks': all_bookmarks[:8], 'bookmark_lists': bookmark_lists, 'user_id': user_id})

def bookmarks_page_view(request, user_id = ""):
    if not user_id or user_id == "None": #TODO: when can this be "None"?
        return render(request, 'a_pages/splash.html')
    
    clear_history(request)
    add_to_history(request, "/profile-view/"+user_id)
    return render(request, 'a_pages/bookmarks.html', {'user_id': user_id})

def bookmarks_view(request, user_id = ""):
    list_id = request.GET.get("list_id", "")
    #TODO: when is this set?
    list_name = request.GET.get("list_name", "")
    
    if list_name:
        request.session['list_name'] = list_name
        
    if not user_id:
        user_id = request.GET.get("user_id", "")
        
    add_to_history(request, "/bookmarks-view/"+user_id)
        
    list_results = get_api_results('lists?list_type=BK&user='+user_id)    
    
    if not list_results:
        return HttpResponseClientRedirect("/")
    
    bookmark_categories = []
    
    for bk_list in list_results["results"]:
        if bk_list["items"]:
            bookmark_categories.append(bk_list)
    
    return render(request, 'includes/bookmarks.html', {'categories': bookmark_categories, 'user_id': user_id, 'list_id': list_id})

def bookmarks_content_view(request):
    list_id = request.GET.get("list_id", "")
    user_id = request.GET.get("user_id", "")
    data = {}
    
    # if no list id, then get all bookmarks
    if not list_id:
        data = get_api_results('items/?list_type=BK&user='+user_id)
    else:
        data = get_api_results('items/?list='+list_id) 
        
    bookmarks = []
    
    for item in data['results']:
        imageurl = item["imageurl"]
                                           
        if item["ref_relation"]:
            item = item["ref_relation"]
            
            # if using ref_relation, we need to still use the top level imageurl
            if imageurl:
                item["imageurl"] = imageurl
            
        item["user"]["profile_pic"] = images_url + item["user"]["profile_pic"]
        bookmarks.append(item)    

    return render(request, 'includes/bookmarks_content.html', {'bookmarks': bookmarks, 'list_id': list_id, 'user_id': user_id})

def share_modal_view(request):
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
            
        return render(request, 'includes/mobile_share_modal.html', {'profile_url': profile_url, 'app_store_url': app_store_url, 'app_store_image': app_store_image, 'app_store_text_image': app_store_text_image})
        
    return render(request, 'includes/share_modal.html', {'profile_url': profile_url, 'full_profile_url': full_profile_url})

def profile_page_view(request, user_id=""):
    if not user_id or user_id == "None":
        return render(request, 'a_pages/splash.html')
    
    clear_history(request)
    return render(request, 'a_pages/profile.html', {'user_id': user_id})

def profile_view(request, user_id=""):
    if not user_id:
        user_id = request.GET.get("user_id", "")
        
    add_to_history(request, "/profile-view/"+user_id)
    
    user = get_profile_data(request.session, user_id)
    user_name = user.get("username", "")
    
    return render(request, 'includes/profile.html', {'user_id': user_id, 'user_name': user_name})

def profile_content_view(request, user_id=""):
    if not user_id:
        user_id = request.GET.get("user_id", "")
        
    user = get_profile_data(request.session, user_id, call_db=True)

    if not user or user.get("error", {}).get("status_code", "") == 404:
        return HttpResponseClientRedirect("/")
    
    #TODO: use Mike's function to create social links
    socials = []
    
    for social in user.get("metadata", {}).get("socials", []):
        social_key = social.get("key", "")
        
        match social_key:
            case "twitter":
                socials.append({'icon':static("twitter.svg")})
            case "facebook":
                socials.append({'icon':static("facebook.svg")})
            case "instagram":
                socials.append({'icon':static("instagram.svg")})
            case "tiktok":
                socials.append({'icon':static("tiktok.svg")})
            case "youtube":
                socials.append({'icon':static("youtube.svg")})
    
    return render(request, 'includes/profile_content.html', {'user': user, 'socials': socials})

def list_page_view(request, list_id=""):
    if not list_id or list_id == "None":
        return render(request, 'a_pages/splash.html')
    
    endpoint = get_api_results('items/?list='+list_id)
    response = requests.get(endpoint)
    
    if not response:
        return redirect("/")
    
    data = response.json()
    
    if (len(data['results']) == 0):
        return render(request, 'a_pages/splash.html')
    
    user_id = data['results'][0]['user']['id']
    list_title = data['results'][0]['list']['title']
    num_links = len(data["results"])
    
    clear_history(request)
    add_to_history(request, "/profile-view/"+user_id)
    
    return render(request, 'a_pages/list.html', {'user_id': user_id, 'list_id': list_id, 'num_links': num_links, 'title': list_title})

def list_content_view(request, list_id=""):
    if not list_id:
        list_id = request.GET.get("list_id", "")
    
    list_result = get_api_results('items/?list='+list_id)
    
    if not list_result:
        return HttpResponseClientRedirect("/")

    if (len(list_result['results']) == 0):
        return HttpResponseClientRedirect("/")
    
    for item in list_result['results']:
            # what default image should be used?
            if not item["imageurl"]:
                item["imageurl"] = "https://images.newscientist.com/wp-content/uploads/2024/05/15214800/SEI_204280908.jpg"
    
    #check for null results, is this the best way to get user and list?
    user_id = list_result['results'][0]['user']['id']
    list_title = list_result['results'][0]['list']['title']
    num_links = len(list_result["results"])
    
    return render(request, 'includes/list_content.html', {'results': list_result["results"], 'list_id': list_id, 'user_id': user_id, 'num_links': num_links, 'title': list_title})

def list_view(request, list_id=""):
    if not list_id:    
        list_id = request.GET.get("list_id", "")
        
    list_name = request.GET.get("list_name", "")
    
    if list_name:
        request.session['list_name'] = list_name
        
    list_name = request.session.get('list_name', '')
    
    add_to_history(request, "/list-view/"+list_id)
    
    return render(request, 'includes/list.html', {'list_id': list_id, 'title': list_name})

def item_page_view(request, item_id=""):
    if not item_id or item_id == "None":
        return render(request, 'a_pages/splash.html')
    
    clear_history(request)
    
    item_result = get_api_results('items/'+item_id)
    
    if not item_result:
        return redirect("/")
    
    list_id = ""
        
    if item_result["ref_relation"]:
        item_result = item_result["ref_relation"]
        
    if item_result["list"]:
        list_id = item_result['list']['id']
        
    user_id = item_result['user']['id']
    user_name = item_result['user']['name']
    add_to_history(request, "/profile-view/"+user_id)
    
    return render(request, 'a_pages/item.html', {'item_id': item_id, 'list_id': list_id, 'user_id': user_id, 'user_name': user_name})

def item_view(request, item_id="", user_id=""):
    if not item_id:    
        item_id = request.GET.get("item_id", "")
        
    if not user_id:    
        user_id = request.GET.get("user_id", "")
        
    add_to_history(request, "/item-view/"+item_id)
    
    return render(request, 'includes/item.html', {'user_id': user_id, 'item_id': item_id})

def item_content_view(request):    
    item_id = request.GET.get('item_id', "")
    item_data = get_api_results('items/'+item_id)
    
    #this seems like the best way to do this
    if item_data["ref_relation"]:
        item_data = item_data["ref_relation"]
        
    item_data["user"]["profile_pic"] = images_url + item_data["user"]["profile_pic"]
    
    #TODO: is imageurl always populated? if not, this is another place that stores the image
    #if not item_data['imageurl'] and item_data['content']:
    #    item_data['imageurl'] = item_data['content'][0].get('file', '')
    
    created = datetime.now() - datetime.strptime(item_data["created"], '%Y-%m-%dT%H:%M:%S.%fZ')
    total_seconds = created.total_seconds()
    minutes = math.ceil(total_seconds / 60)
    
    # I'll be revisiting this once we know what to display
    if minutes < 60:
        created = "%m mins" % (minutes)
    else:
        hours = math.ceil(minutes / 60)
        if hours < 24:
            created = "%h hrs" % (hours)
        else:
            days = math.ceil(hours / 24)
            if days < 365:
                created = "%d days" % (days)
            else:
                years = math.floor(days / 365)
                created = "%y years" % (years)
    
    return render(request, 'includes/item_content.html', {'item': item_data, 'user': item_data["user"], 'created': created})

def more_items_view(request):
    item_id = request.GET.get("item_id")
    user_id = request.GET.get("user_id")
    
    user = get_profile_data(request.session, user_id, call_db=True)
    user_name = user["name"]
    
    #TODO: page_size is being ignored 10/15
    data = get_api_results('items/?page_size=6&user='+user_id)
    items = []
    
    for item in data['results']:
            if item["ref_relation"]:
                item = item["ref_relation"]            
                
            if item["id"] != item_id:
                items.append(item)
    
    return render(request, 'includes/more_items.html', {'items': items[:6], 'user_id': user_id, 'user_name': user_name})

def item_page(request):    
    item_id = request.GET['item_id']
    data = get_api_results('items/'+item_id)
    
    return render(request, 'includes/item_page.html', {'item': data})