from django.views import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from keeplist_website.api.component_views import *
from keeplist_website.api.page_views import *

class ProfileView(View):
    def get(self, request, user_id):
        user = get_user_profile(user_id)
        if not user:
            return HttpResponseRedirect('/')
        return render(request, 'a_pages/profile.html', {'user': user})
