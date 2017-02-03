from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import datetime, requests, json

INVALID_ERROR = {'flag_error':True,
                 'message':"Invalid url, Please try again" }

LIMIT_EXECEEDED = {'flag_error':True,
                  'message': "API access limit exceeded",
                  'message_body':"Please try after some time" }

INVALID_REPO = {'flag_error':True,
                'message':"Invalid repository or user, Please try again"}

API = "https://api.github.com/repos/"
WARN = "API rate limit exceeded"
WARN_NOT_FOUND = "Not Found"

time_format = "%Y-%m-%dT%H:%M:%SZ"
delta_24_hrs = datetime.timedelta(days=1)
delta_7_days = datetime.timedelta(days=7)

@method_decorator(csrf_exempt, name='dispatch')
class HomePage(View):

    def get(self, request):
        '''
        handles the get request, displays home page
        '''
        return render(request, 'openissues/home.html')

    def post(self, request):
        '''
        handles the post request,
        makes github api call
        calculates open issues and displays it in home page
        '''
        link = request.POST.get('url', None)
        # splits the url to list of strings
        url_list = link.split('/')
        try:
            for words in url_list:
                if 'github.com' in words:
                    index = url_list.index(words)
            # if 'github.com' is present takes the next two strings
            # as 'owner name' and 'repo name'
            owner, repo = url_list[index+1], url_list[index+2]
        except Exception:
            return self.error(request, INVALID_ERROR)

        # formats url to make github api call
        api = API + owner + '/' + repo + '/issues?status=open&page='
        open_issues, pagination = 0, 0
        open_more_than_7_days_ago, open_day_before = 0, 0
        open_btw_24_and_7, open_in_the_last_7_days = 0, 0

        today = datetime.datetime.utcnow().date()
        # initializes the timedelta for 1 day and  7 days
        limit_24 = today - delta_24_hrs
        limit_7 = today - delta_7_days

        issues_list = []

        # tries github api call until json returns empty or api limit exceeds
        while(True):
            pagination += 1
            final_url = api + str(pagination)
            api_response = requests.get(final_url)
            data = json.loads(api_response.text)
            if(len(data) == 0):
                break
            elif WARN in str(data):
                return self.error(request, LIMIT_EXECEEDED)
            elif WARN_NOT_FOUND in str(data):
                return self.error(request, INVALID_REPO)
            open_issues += len(data)
            issues_list.extend(data)

        for issue in issues_list:
            # takes 'issue create time' from list
            create_time = datetime.datetime.strptime(issue["created_at"], time_format).date()
            # checks issue duration and increments corresponding variables
            if(create_time < limit_24):
                open_day_before += 1
            if(create_time >= limit_7):
                open_in_the_last_7_days += 1
            if(create_time < limit_7):
                open_more_than_7_days_ago += 1

        last_24_hrs = open_issues - open_day_before
        btw_24_and_7 = open_in_the_last_7_days - last_24_hrs

        context = {'flag_post':True,
                   'open_issues': open_issues,
                   'last_24_hrs': open_issues - open_day_before,
                   'btw_24_and_7': btw_24_and_7,
                   'more_than_7': open_more_than_7_days_ago }

        return render(request, 'openissues/home.html', context)

    def error(self, request, message):
        '''
        view returning home page with 'error' placeholder
        '''
        return render(request, 'openissues/home.html', message)
