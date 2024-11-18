from django.db import models

class RecordedSession(models.Model):
    session_name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    data = models.JSONField()

    def __str__(self):
        return self.session_name
