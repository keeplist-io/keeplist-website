"""
URL configuration for a_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from keeplist_website.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', splash_page_view),
    path('search/', splash_page_view),
    path('notifications/', splash_page_view),
    path('profile/', splash_page_view),
    
    path('profile/<str:user_id>/', profile_page_view),
    path('list/<str:list_id>/', list_page_view),
    path('item/<str:item_id>/', item_page_view),
    
    path('menu-view/', menu_view, name="menu_view"),
    path('mobile-menu-view/', mobile_menu_view, name="mobile_menu_view"),
    path('mobile-splash-content-view/', mobile_splash_content_view, name="mobile_splash_content_view"),
    path('keeplist-preview-view/', keeplist_preview_view, name="keeplist_preview_view"),
    path('bookmarks-preview-view/', bookmarks_preview_view, name="bookmarks_preview_view"),
    path('bookmarks-list-view/', bookmarks_list_view, name="bookmarks_list_view"),
    path('bookmarks-content-view/', bookmarks_content_view, name="bookmarks_content_view"),
    path('list-view/', list_view, name="list_view"),
    path('list-view/<str:list_id>', list_view),
    path('list-content-view/', list_content_view, name="list_content_view"),
    path('item-view/', item_view, name="item_view"),
    path('item-view/<str:item_id>', item_view, name="item_view"),
    path('item-content-view/', item_content_view, name="item_content_view"),
    path('more-items-view/', more_items_view, name="more_items_view"),
    path('header-content-view/', header_content_view, name="header_content_view"),
    path('profile-view/', profile_view, name="profile_view"),
    path('profile-view/<str:user_id>', profile_view),
    path('profile-content-view/', profile_content_view, name="profile_content_view"),
    path('profile-header-view/', profile_header_view, name="profile_header_view"),
    path('share-modal-view/', share_modal_view, name="share_modal_view"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
