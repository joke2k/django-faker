from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^preview.html$', TemplateView.as_view(template_name='faker/preview.html'))
]
