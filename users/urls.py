from rest_framework.routers import DefaultRouter
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import  UserViewSet,CustomObtainTokenPairView, dashboard,login_view


user_router = DefaultRouter()
user_router.register(r'users', UserViewSet, basename='users')




urlpatterns = [
    path("token/request/", CustomObtainTokenPairView.as_view(), name="token_request"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"), 
    path('dashboard/', dashboard, name='dashboard'),
    path('', login_view, name='login'),
    
]

urlpatterns += user_router.urls