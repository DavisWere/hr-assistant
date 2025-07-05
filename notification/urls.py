from rest_framework.routers import DefaultRouter
from django.urls import path
from notification.views import mistral_chat_view, ChatHistoryViewSet

notification_router= DefaultRouter()

notification_router.register(r'chat/history', ChatHistoryViewSet)

urlpatterns = [  
    path('chat/', mistral_chat_view, name='mistral-chat'),
]
urlpatterns += notification_router.urls

