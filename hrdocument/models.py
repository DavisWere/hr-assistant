from django.db import models

from django.db import models
from django.utils import timezone

class HRDocument(models.Model):
    title = models.CharField(max_length=255, help_text="Title of the document")
    content = models.TextField(help_text="Full document text (used for AI search)")
    uploaded_at = models.DateTimeField(default=timezone.now, help_text="Upload time of the document")

    def __str__(self):
        return self.title

