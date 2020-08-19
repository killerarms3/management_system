from django.db import models
from django.contrib.contenttypes.models import ContentType
# Create your models here.
class Language(models.Model):
    language = models.CharField(max_length=5)
    status = models.BooleanField(default=1)

class Code(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete='CASCADE')
    code = models.CharField(max_length=36)
    zh_TW = models.CharField(max_length=36)


