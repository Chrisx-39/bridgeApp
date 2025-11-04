from django.urls import path
from . import views

urlpatterns = [
    # ---------------------------
    # 1. Core Bridge Management
    # ---------------------------
    path('', views.dashboard_view, name='dashboard'),
    path('bridges/', views.BridgeListView.as_view(), name='bridge_list'),
    path('bridges/<int:pk>/', views.BridgeDetailView.as_view(), name='bridge_detail'),
    path('bridges/create/', views.BridgeCreateView.as_view(), name='bridge_create'),
    path('bridges/<int:pk>/edit/', views.BridgeUpdateView.as_view(), name='bridge_edit'),
    path('bridges/<int:pk>/delete/', views.BridgeDeleteView.as_view(), name='bridge_delete'),

    # ---------------------------
    # 2. Maintenance Record Management
    # ---------------------------
    path('bridges/<int:bridge_pk>/maintenance/add/',
         views.MaintenanceRecordCreateView.as_view(),
         name='maintenance_record_create'),

    path('maintenance/<int:pk>/edit/',
         views.MaintenanceRecordUpdateView.as_view(),
         name='maintenance_record_update'),

    path('maintenance/<int:pk>/delete/',
         views.MaintenanceRecordDeleteView.as_view(),
         name='maintenance_record_delete'),

    # ---------------------------
    # 3. Traffic Data Management
    # Uses 'bridge_pk' to identify which bridge's traffic data to create/update.
    # The view handles both creation and updating via the same URL.
    # ---------------------------
    path('bridges/<int:bridge_pk>/traffic/manage/',
         views.TrafficDataCreateUpdateView.as_view(),
         name='traffic_data_manage'),
]
