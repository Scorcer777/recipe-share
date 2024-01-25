from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from users.views import ProfileViewSet
from .views import TagViewSet, IngredientViewSet, RecipeViewSet


router_v1 = DefaultRouter()

router_v1.register('users', ProfileViewSet, basename='users')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('users/subscriptions/',
         ProfileViewSet.as_view({'get': 'subscriptions'}),
         name='user-subscriptions'),
    path('users/me/',
         ProfileViewSet.as_view({'get': 'me'}),
         name='user-me'),
    path('', include('djoser.urls')),
    path('', include(router_v1.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
