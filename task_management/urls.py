from django.contrib import admin
from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import home,no_permission 

urlpatterns = [
    path('admin/', admin.site.urls),
    path("tasks/", include("tasks.urls")),
    path("users/", include("users.urls")),
    path("",home, name="home"),
    path("no-permission",no_permission, name="no-permission"),
] + debug_toolbar_urls()

# ⭐ মিডিয়া ফাইল সার্ভ করার জন্য
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

