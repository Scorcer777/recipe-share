from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, TagViewSet, IngredientViewSet, RecipeViewSet

app_name = 'api'

router_v1 = DefaultRouter()


router_v1.register('users', UserViewSet, basename='users')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('users/subscriptions/', UserViewSet.as_view({'get': 'subscriptions'}),
         name='user-subscriptions'),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
]
