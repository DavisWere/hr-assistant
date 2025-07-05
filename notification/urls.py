from rest_framework.routers import DefaultRouter
from django.urls import path
from notification.views import MistralChatView, ChatHistoryViewSet

notification_router= DefaultRouter()

notification_router.register(r'chat/history', ChatHistoryViewSet)

urlpatterns = [ 
    path('chat/', MistralChatView.as_view(), name='chat-with-mistral'),  
]
urlpatterns += notification_router.urls

