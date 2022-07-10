from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from website.views import PostList, PostDetail


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name="pages/maintenance.html"), name="maintenance"),
    path('home/', TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path('blog/', PostList.as_view(), name='blog-list'),
    path('blog/<slug:slug>/', PostDetail.as_view(), name='post'),
    path('about/', TemplateView.as_view(template_name="pages/about.html"), name="about"),
]
