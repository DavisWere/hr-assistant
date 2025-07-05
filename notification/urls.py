from rest_framework.routers import DefaultRouter
from django.urls import path
from notification.views import MistralChatView

notification_router= DefaultRouter()


urlpatterns = [ 
    path('chat/', MistralChatView.as_view(), name='chat-with-mistral'),  
]
urlpatterns += notification_router.urls

