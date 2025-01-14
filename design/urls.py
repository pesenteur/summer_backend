from django.urls import path
from .views import *

urlpatterns = [
    path('designs', DesignListCreateView.as_view()),
    path('design/cancel-preview', cancel_preview_view),
    path('design/preview', get_preview_view),
    path('design/<str:pk>', DesignRetrieveUpdateDestroyView.as_view()),
    path('design-versions', DesignHistoryListCreateView.as_view()),
    path('design/<str:pk>/generate-preview', generate_preview_view),
]