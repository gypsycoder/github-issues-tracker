from django.shortcuts import render
from django.views import View

class HomePage(View):

    def get(self, request):
        return render(request, 'openissues/home.html')
