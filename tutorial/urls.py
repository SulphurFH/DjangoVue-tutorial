"""tutorial URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import xadmin
from django.conf.urls import url, include
from django.views.generic import TemplateView
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token

from users.views import UserViewset
from books.views import BooksListView, BookDetailView, BooksCategoryListView


router = DefaultRouter()

router.register(r'users', UserViewset, base_name="users")

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^index/', TemplateView.as_view(template_name="index.html"), name="index"),
    url(r'docs/', include_docs_urls(title="tutorial")),
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # drf自带的token认证模式
    url(r'^api-token-auth/', views.obtain_auth_token),
    # jwt的认证接口
    url(r'^login/', obtain_jwt_token),
    # Book
    url(r'^books/$', BooksListView.as_view(), name='books'),
    url(r'^books/(?P<pk>[0-9]+)/$', BookDetailView.as_view()),
    url(r'^books-category/', BooksCategoryListView.as_view(), name='books_category'),
]
