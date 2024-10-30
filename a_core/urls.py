from django.urls import path, re_path
from keeplist_website.views import *
from django.conf import settings
from django.conf.urls.static import static

user_routes = [
    path('', splash_page_view, name="splash_page_view"),
    re_path(r'^(?:u|user|profile)/$', splash_page_view, name="splash_page_view"),
    
    re_path(r'^(?:u|user|profile)/(?P<user_id>@?[\w-]+)/$', profile_page_view, name="profile_page_view"),
    re_path(r'^(?:u|user|profile)/(?P<user_id>@?[\w-]+)/(?:lists|keeps)/$', profile_page_view, name="profile_page_view"),
    re_path(r'^(?:u|user|profile)/(?P<user_id>@?[\w-]+)/(?:lists|l)/(?P<list_id>[\w-]+)/$', 
        list_page_view, name="list_page_view"),
    re_path(r'^(?:u|user|profile)/(?P<user_id>@?[\w-]+)/(?:keeps|k)/(?P<list_id>[\w-]+)/$',
        bookmarks_page_view, name="bookmarks_page_view"),
    
    re_path(r'^(?:u|user|profile)/(?P<user_id>@?[\w-]+)/(?P<list_type>[\w-]+)/(?P<list_id>[\w-]+)/(?P<item_id>[\w-]+)/$',
        item_page_view, name="item_page_view"),
]

urlpatterns = [
    *user_routes,
    *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
    path('components/menu-view/', menu_view, name="menu_view"),
    path('components/mobile-menu-view/', mobile_menu_view, name="mobile_menu_view"),
    path('components/mobile-splash-content-view/', mobile_splash_content_view, name="mobile_splash_content_view"),
    path('components/keeplist-preview-view/<str:user_id>/', keeplist_preview_view, name="keeplist_preview_view"),
    path('components/bookmarks-preview-view/<str:user_id>/', bookmarks_preview_view, name="bookmarks_preview_view"),
    path('components/bookmarks-view/<str:user_id>/', bookmarks_view, name="bookmarks_view"),
    path('components/bookmarks-content-view/<str:user_id>/<str:list_id>/', bookmarks_content_view, name="bookmarks_content_view"),
    path('components/list-view/<str:user_id>/<str:list_type>/<str:list_id>', list_view, name="list_view"),
    path('components/list-content-view/<str:user_id>/<str:list_type>/<str:list_id>', list_content_view, name="list_content_view"),
    path('components/item-view/<str:user_id>/<str:list_type>/<str:list_id>/<str:item_id>', item_view, name="item_view"),
    path('components/item-content-view/<str:user_id>/<str:list_type>/<str:list_id>/<str:item_id>', item_content_view, name="item_content_view"),
    path('components/more-items-view/<str:user_id>/<str:list_type>', more_items_view, name="more_items_view"),
    path('components/header-content-view/', header_content_view, name="header_content_view"),
    path('components/profile-view/<str:user_id>/', profile_view, name="profile_view"),
    path('components/profile-content-view/<str:user_id>/', profile_content_view, name="profile_content_view"),
    path('components/share-modal-view/', share_modal_view, name="share_modal_view"),
] 
