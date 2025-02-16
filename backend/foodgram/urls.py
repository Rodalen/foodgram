from django.contrib import admin
from django.urls import include, path

from recipes.views import redirect_from_short_link


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<str:short_link>/', redirect_from_short_link, name='redirect_from_short_link'),
]
