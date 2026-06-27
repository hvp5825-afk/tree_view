from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('network/', include('network.urls')),
    path('kyc/', include('kyc.urls')),
    path('pmf/', include('pmf.urls')),
    path('helpdesk/', include('helpdesk.urls')),
    path('rewards/', include('rewards.urls')),
    path('support/', include('support.urls')),
    path('notifications/', include('notifications.urls')),
    path('products/', include('products.urls')),
    path('reports/', include('reports.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
