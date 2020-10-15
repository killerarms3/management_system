from django.db import models
from django.contrib.contenttypes.models import ContentType
# Create your models here.
class Code(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete='CASCADE')
    code = models.CharField(max_length=36)
    name = models.CharField(max_length=36)