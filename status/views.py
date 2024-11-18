from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import RecordedSession
# Create your views here.
def index(request):
    return HttpResponse("hello")



def get_recorded_sessions(request):
    sessions = RecordedSession.objects.all().values('id', 'session_name', 'start_time', 'end_time')
    return JsonResponse({'sessions': list(sessions)})

