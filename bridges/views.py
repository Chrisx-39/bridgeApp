from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.db import transaction
from .models import Bridge, TrafficData, MaintenanceRecord
from .forms import BridgeForm, TrafficDataForm, MaintenanceRecordForm
from django.views.generic.edit import BaseUpdateView # Import needed if not fully imported above

# --- Bridge Management Views ---

class BridgeListView(ListView):
    model = Bridge
    template_name = 'bridges/bridge_list.html'
    context_object_name = 'bridges'
    paginate_by = 10

    def get_queryset(self):
        # Prefetch related traffic data to avoid N+1 queries in the list view
        queryset = super().get_queryset().select_related('traffic')
        search = self.request.GET.get('search')
        condition = self.request.GET.get('condition')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(route__icontains=search)
            )

        if condition:
            # Note: Filtering based on a calculated property like condition_category is inefficient.
            # For a large enterprise system, this calculation should ideally be stored/cached 
            # or performed via annotations if possible.
            filtered = []
            for bridge in queryset:
                if bridge.condition_category.upper().replace(' ', '_') == condition:
                    filtered.append(bridge.id)
            queryset = queryset.filter(id__in=filtered)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_bridges'] = Bridge.objects.count()
        context['search_query'] = self.request.GET.get('search', '')
        context['condition_filter'] = self.request.GET.get('condition', '')
        return context


class BridgeDetailView(DetailView):
    model = Bridge
    template_name = 'bridges/bridge_detail.html'
    context_object_name = 'bridge'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the traffic data object explicitly
        try:
            context['traffic_data'] = self.object.traffic
        except TrafficData.DoesNotExist:
            context['traffic_data'] = None
            
        # Get all maintenance records for display, perhaps with a separate link for 'All Records'
        context['maintenance_records'] = self.object.maintenance_records.all()[:5]
        return context


class BridgeCreateView(CreateView):
    model = Bridge
    form_class = BridgeForm
    template_name = 'bridges/bridge_form.html'
    success_url = reverse_lazy('bridge_list')

    def form_valid(self, form):
        messages.success(self.request, 'Bridge created successfully!')
        return super().form_valid(form)


class BridgeUpdateView(UpdateView):
    model = Bridge
    form_class = BridgeForm
    template_name = 'bridges/bridge_form.html'
    success_url = reverse_lazy('bridge_list')

    def form_valid(self, form):
        messages.success(self.request, 'Bridge updated successfully!')
        return super().form_valid(form)


class BridgeDeleteView(DeleteView):
    model = Bridge
    template_name = 'bridges/bridge_confirm_delete.html'
    success_url = reverse_lazy('bridge_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Bridge deleted successfully!')
        return super().delete(request, *args, **kwargs)


# --- Maintenance Record Management Views ---

class MaintenanceRecordMixin:
    model = MaintenanceRecord
    form_class = MaintenanceRecordForm

    def get_success_url(self):
        # Redirect back to the detail page of the bridge
        bridge_pk = self.object.bridge.pk
        return reverse('bridge_detail', kwargs={'pk': bridge_pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ensure the parent bridge is available in the context for template links/titles
        if 'bridge_pk' in self.kwargs:
            context['bridge'] = get_object_or_404(Bridge, pk=self.kwargs['bridge_pk'])
        elif self.object:
            context['bridge'] = self.object.bridge
        return context


class MaintenanceRecordCreateView(MaintenanceRecordMixin, CreateView):
    template_name = 'bridges/maintenance_record_form.html'

    def form_valid(self, form):
        # Link the new record to the Bridge specified in the URL kwargs
        bridge = get_object_or_404(Bridge, pk=self.kwargs['bridge_pk'])
        form.instance.bridge = bridge
        messages.success(self.request, f'Maintenance action for {bridge.name} scheduled successfully.')
        return super().form_valid(form)


class MaintenanceRecordUpdateView(MaintenanceRecordMixin, UpdateView):
    template_name = 'bridges/maintenance_record_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Maintenance record updated successfully.')
        return super().form_valid(form)


class MaintenanceRecordDeleteView(MaintenanceRecordMixin, DeleteView):
    template_name = 'bridges/maintenance_record_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        # Capture bridge ID before deletion
        bridge_pk = self.get_object().bridge.pk
        messages.success(self.request, 'Maintenance record deleted successfully.')
        self.success_url = reverse('bridge_detail', kwargs={'pk': bridge_pk})
        return super().delete(request, *args, **kwargs)


# --- Traffic Data Management Views (New) ---

class TrafficDataMixin:
    model = TrafficData
    form_class = TrafficDataForm

    def get_success_url(self):
        # Redirect back to the detail page of the bridge
        # TrafficData is OneToOne, so self.object.bridge exists
        bridge_pk = self.object.bridge.pk
        return reverse('bridge_detail', kwargs={'pk': bridge_pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'bridge_pk' in self.kwargs:
            context['bridge'] = get_object_or_404(Bridge, pk=self.kwargs['bridge_pk'])
        elif self.object:
            context['bridge'] = self.object.bridge
        return context

class TrafficDataCreateUpdateView(TrafficDataMixin, BaseUpdateView):
    """
    Handles both creation and updating of TrafficData because it's a OneToOne field.
    If it exists, it updates; if not, it creates.
    """
    template_name = 'bridges/traffic_data_form.html'
    
    def get_object(self, queryset=None):
        bridge_pk = self.kwargs.get('bridge_pk')
        bridge = get_object_or_404(Bridge, pk=bridge_pk)
        
        # Try to get the existing TrafficData object, if it exists
        try:
            return TrafficData.objects.get(bridge=bridge)
        except TrafficData.DoesNotExist:
            # If it doesn't exist, return a new instance tied to the bridge
            return TrafficData(bridge=bridge)

    def form_valid(self, form):
        if form.instance.pk:
            messages.success(self.request, 'Traffic data updated successfully!')
        else:
            messages.success(self.request, 'Traffic data recorded successfully!')
        return super().form_valid(form)


# --- Dashboard and Analytics View (Enhanced) ---

def dashboard_view(request):
    total_bridges = Bridge.objects.count()
    bridges = Bridge.objects.all()

    # Calculate condition statistics (existing logic)
    condition_stats = {
        'excellent': 0, 'very_good': 0, 'good': 0, 'fair': 0, 'poor': 0
    }
    for bridge in bridges:
        category = bridge.condition_category.lower().replace(' ', '_')
        if category in condition_stats:
            condition_stats[category] += 1

    # --- NEW: Traffic Analytics ---
    # Annotate to get total vehicles across all bridges efficiently
    traffic_queryset = TrafficData.objects.aggregate(
        total_heavy=Avg('heavy_vehicles'),
        total_small=Avg('small_vehicles'),
        total_bridges_with_traffic=Count('bridge')
    )
    
    avg_daily_heavy = int(traffic_queryset.get('total_heavy') or 0)
    avg_daily_small = int(traffic_queryset.get('total_small') or 0)
    
    # --- NEW: Maintenance Analytics ---
    total_maintenance_actions = MaintenanceRecord.objects.count()
    completed_maintenance = MaintenanceRecord.objects.filter(is_completed=True).count()
    completion_rate = round((completed_maintenance / total_maintenance_actions) * 100, 1) if total_maintenance_actions > 0 else 0


    recent_maintenance = MaintenanceRecord.objects.select_related('bridge').order_by('-created_at')[:5]

    context = {
        'total_bridges': total_bridges,
        'condition_stats': condition_stats,
        'recent_maintenance': recent_maintenance,
        
        # New Analytics Data
        'avg_daily_traffic': avg_daily_heavy + avg_daily_small,
        'total_maintenance_actions': total_maintenance_actions,
        'completion_rate': completion_rate,
    }
    return render(request, 'bridges/dashboard.html', context)

