from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, CHANGE, ADDITION, DELETION

class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, blank=False, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=False)
    action_flag = models.CharField(max_length=5)
    change_message = models.TextField()
    date = models.DateTimeField()
# Create your models here.