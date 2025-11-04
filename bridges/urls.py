from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('bridges/', views.BridgeListView.as_view(), name='bridge_list'),
    path('bridges/<int:pk>/', views.BridgeDetailView.as_view(), name='bridge_detail'),
    path('bridges/create/', views.BridgeCreateView.as_view(), name='bridge_create'),
    path('bridges/<int:pk>/edit/', views.BridgeUpdateView.as_view(), name='bridge_edit'),
    path('bridges/<int:pk>/delete/', views.BridgeDeleteView.as_view(), name='bridge_delete'),
]

