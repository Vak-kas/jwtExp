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



def get_recorded_session_detail(request, session_id):
    try:
        session = RecordedSession.objects.get(id=session_id)
        return JsonResponse({
            'session_name': session.session_name,
            'start_time': session.start_time,
            'end_time': session.end_time,
            'data': session.data
        })
    except RecordedSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
