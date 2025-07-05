from django.contrib import admin
from .models import KnowledgeBaseArticle, EscalationRequest

admin.site.register(KnowledgeBaseArticle)
admin.site.register(EscalationRequest)