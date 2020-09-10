from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, blank=False, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=False)
    action_flag = models.CharField(max_length=5)
    change_message = models.TextField()
    date = models.DateTimeField()

    class Meta:
        permissions = [('can_view_self_history', 'can view self history'),]

# Create your models here.