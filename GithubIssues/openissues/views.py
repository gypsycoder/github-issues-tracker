from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import datetime, requests, json

INVALID_ERROR = {'error':True, 'message':"Invalid url, Please try again"}

API = "https://api.github.com/repos/"

time_format = "%Y-%m-%dT%H:%M:%SZ"
delta_24_hrs = datetime.timedelta(days=1)
delta_7_days = datetime.timedelta(days=7)

@method_decorator(csrf_exempt, name='dispatch')
class HomePage(View):

    def get(self, request):
        return render(request, 'openissues/home.html')

    def post(self, request):
        link = request.POST.get('url', None)
        url_list = link.split('/')
        try:
            for words in url_list:
                if 'github.com' in words:
                    index = url_list.index(words)
            owner, repo = url_list[index+1], url_list[index+2]
        except UnboundLocalError:
            return self.error(request, INVALID_ERROR)

        api = API + owner + '/' + repo + '/issues?status=open&page='
        open_issues, count = 0, 0
        open_more_than_7_days_ago, open_day_before = 0, 0
        open_btw_24_and_7, open_in_the_last_7_days = 0, 0

        today = datetime.datetime.utcnow().date()
        limit_24 = today - delta_24_hrs
        limit_7 = today - delta_7_days

        issues_list = []

        while(True):
            count += 1
            final_url = api + str(count)
            print(final_url)
            api_response = requests.get(final_url)
            data = json.loads(api_response.text)
            if(len(data) == 0):
                break
            open_issues += len(data)
            issues_list.extend(data)

        for issue in issues_list:
            create_time = datetime.datetime.strptime(issue["created_at"], time_format).date()
            if(create_time < limit_24):
                open_day_before += 1
            if(create_time >= limit_7):
                open_in_the_last_7_days += 1
            if(create_time < limit_7):
                open_more_than_7_days_ago += 1

        last_24_hrs = open_issues - open_day_before
        btw_24_and_7 = open_in_the_last_7_days - last_24_hrs

        context = {'post':True,
                   'open_issues': open_issues,
                   'last_24_hrs': open_issues - open_day_before,
                   'btw_24_and_7': btw_24_and_7,
                   'more_than_7': open_more_than_7_days_ago }

        return render(request, 'openissues/home.html', context)

    def error(self, request, message):
        return render(request, 'openissues/home.html', message)
