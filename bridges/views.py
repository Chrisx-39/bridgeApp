from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg
from django.db import transaction
from .models import Bridge, TrafficData, MaintenanceRecord
from .forms import BridgeForm, TrafficDataForm, MaintenanceRecordForm
from django.views.generic.edit import BaseUpdateView # Import needed if not fully imported above

# --- Bridge Management Views ---

class BridgeListView(LoginRequiredMixin, ListView):
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


class BridgeDetailView(LoginRequiredMixin, DetailView):
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


class BridgeCreateView(LoginRequiredMixin, CreateView):
    model = Bridge
    form_class = BridgeForm
    template_name = 'bridges/bridge_form.html'
    success_url = reverse_lazy('bridge_list')

    def form_valid(self, form):
        messages.success(self.request, 'Bridge created successfully!')
        return super().form_valid(form)


class BridgeUpdateView(LoginRequiredMixin, UpdateView):
    model = Bridge
    form_class = BridgeForm
    template_name = 'bridges/bridge_form.html'
    success_url = reverse_lazy('bridge_list')

    def form_valid(self, form):
        messages.success(self.request, 'Bridge updated successfully!')
        return super().form_valid(form)


class BridgeDeleteView(LoginRequiredMixin, DeleteView):
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


class MaintenanceRecordCreateView(LoginRequiredMixin, MaintenanceRecordMixin, CreateView):
    template_name = 'bridges/maintenance_record_form.html'

    def form_valid(self, form):
        # Link the new record to the Bridge specified in the URL kwargs
        bridge = get_object_or_404(Bridge, pk=self.kwargs['bridge_pk'])
        form.instance.bridge = bridge
        messages.success(self.request, f'Maintenance action for {bridge.name} scheduled successfully.')
        return super().form_valid(form)


class MaintenanceRecordUpdateView(LoginRequiredMixin, MaintenanceRecordMixin, UpdateView):
    template_name = 'bridges/maintenance_record_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Maintenance record updated successfully.')
        return super().form_valid(form)


class MaintenanceRecordDeleteView(LoginRequiredMixin, MaintenanceRecordMixin, DeleteView):
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
class TrafficDataCreateUpdateView(LoginRequiredMixin, TrafficDataMixin, UpdateView):
    """
    Handles both creation and updating of TrafficData. 
    Inheriting from UpdateView provides the necessary rendering methods.
    """
    template_name = 'bridges/traffic_data_form.html'
    
    # NOTE: The UpdateView requires self.object to be set for render_to_response 
    # to work correctly, which the base UpdateView.get() method does.
    
    def get_object(self, queryset=None):
        bridge_pk = self.kwargs.get('bridge_pk')
        bridge = get_object_or_404(Bridge, pk=bridge_pk)
        
        # Try to get the existing TrafficData object
        try:
            # If object exists, UpdateView logic continues normally
            return TrafficData.objects.get(bridge=bridge)
        except TrafficData.DoesNotExist:
            # If it doesn't exist, return a new instance tied to the bridge.
            # UpdateView treats a new, non-saved instance as an object to be created.
            return TrafficData(bridge=bridge)

    def form_valid(self, form):
        # We need to save the object manually to check if it was new
        is_new = form.instance.pk is None
        self.object = form.save() # Save the object, setting the pk if new
        
        if is_new:
            messages.success(self.request, 'Traffic data recorded successfully!')
        else:
            messages.success(self.request, 'Traffic data updated successfully!')
            
        # Call super().form_valid(form) is usually preferred, but since we overrode 
        # the save to check for new/update, we manually call the redirect.
        # Ensure TrafficDataMixin provides get_success_url() or success_url attribute.
        return super(UpdateView, self).form_valid(form) 
        # OR simply:
        # return HttpResponseRedirect(self.get_success_url())

# --- Dashboard and Analytics View (Enhanced) ---
@login_required
def dashboard_view(request):
    total_bridges = Bridge.objects.count()
    bridges = Bridge.objects.all()

    # Calculate condition statistics (existing logic)
    raw_condition_stats = {
        'excellent': 0, 'very_good': 0, 'good': 0, 'fair': 0, 'poor': 0
    }
    for bridge in bridges:
        # Assuming condition_category is a model field like 'Excellent Condition'
        category = bridge.condition_category.lower().replace(' ', '_')
        if category in raw_condition_stats:
            raw_condition_stats[category] += 1

    # --- FIX: Pre-process condition_stats to include percentage ---
    processed_condition_stats = {}
    if total_bridges > 0:
        for category, count in raw_condition_stats.items():
            percentage = round((count / total_bridges) * 100, 1)
            # Store the data in a structure the template can easily read
            processed_condition_stats[category] = {
                'count': count,
                'percentage': percentage, # Storing as a number (e.g., 25.5)
            }
    else:
        # Handle the case where there are no bridges
        for category, count in raw_condition_stats.items():
             processed_condition_stats[category] = {'count': 0, 'percentage': 0.0}

    # --- Traffic Analytics ---
    traffic_queryset = TrafficData.objects.aggregate(
        avg_heavy=Avg('heavy_vehicles'),
        avg_small=Avg('small_vehicles'),
    )
    
    # Calculate combined average daily traffic
    avg_daily_heavy = traffic_queryset.get('avg_heavy') or 0
    avg_daily_small = traffic_queryset.get('avg_small') or 0
    avg_daily_traffic = int(avg_daily_heavy + avg_daily_small)
    
    # --- Maintenance Analytics ---
    total_maintenance_actions = MaintenanceRecord.objects.count()
    completed_maintenance = MaintenanceRecord.objects.filter(is_completed=True).count()
    completion_rate = round((completed_maintenance / total_maintenance_actions) * 100, 1) if total_maintenance_actions > 0 else 0

    recent_maintenance = MaintenanceRecord.objects.select_related('bridge').order_by('-created_at')[:5]

    context = {
        'total_bridges': total_bridges,
        'condition_stats': processed_condition_stats,  # Use the pre-processed data
        'recent_maintenance': recent_maintenance,
        
        # Analytics Data
        'avg_daily_traffic': avg_daily_traffic,
        'total_maintenance_actions': total_maintenance_actions,
        'completion_rate': completion_rate,
    }
    return render(request, 'bridges/dashboard.html', context)