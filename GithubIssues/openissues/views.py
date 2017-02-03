from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class HomePage(View):

    def get(self, request):
        return render(request, 'openissues/home.html')

    def post(self, request):
        return render(request, 'openissues/home.html')
