from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Count, Avg
from .models import Bridge, TrafficData, MaintenanceRecord
from .forms import BridgeForm, TrafficDataForm, MaintenanceRecordForm
from django.db import transaction
from django.views.generic.edit import 


class BridgeListView(ListView):
    model = Bridge
    template_name = 'bridges/bridge_list.html'
    context_object_name = 'bridges'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        condition = self.request.GET.get('condition')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(route__icontains=search)
            )
        
        if condition:
            # Filter by condition category
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


def dashboard_view(request):
    total_bridges = Bridge.objects.count()
    bridges = Bridge.objects.all()
    
    # Calculate condition statistics
    condition_stats = {
        'excellent': 0, 'very_good': 0, 'good': 0, 'fair': 0, 'poor': 0
    }
    
    for bridge in bridges:
        category = bridge.condition_category.lower().replace(' ', '_')
        if category in condition_stats:
            condition_stats[category] += 1
    
    recent_maintenance = MaintenanceRecord.objects.select_related('bridge').order_by('-created_at')[:5]
    
    context = {
        'total_bridges': total_bridges,
        'condition_stats': condition_stats,
        'recent_maintenance': recent_maintenance,
    }
    return render(request, 'bridges/dashboard.html', context)


# --- Mixin for Maintenance Record Views ---
class MaintenanceRecordMixin:
    model = MaintenanceRecord
    form_class = MaintenanceRecordForm
    # We define get_success_url in the mixin to ensure we redirect back to the bridge detail
    
    def get_success_url(self):
        # The bridge ID is available on the form instance after validation/creation
        bridge_pk = self.object.bridge.pk
        return reverse('bridge_detail', kwargs={'pk': bridge_pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the parent bridge object to the context for use in the template
        if 'bridge' in self.kwargs:
            context['bridge'] = get_object_or_404(Bridge, pk=self.kwargs['bridge'])
        else:
            context['bridge'] = self.object.bridge
        return context


# --- Maintenance Record Create View ---
class MaintenanceRecordCreateView(MaintenanceRecordMixin, CreateView):
    template_name = 'bridges/maintenance_record_form.html'

    def form_valid(self, form):
        # Link the new record to the Bridge specified in the URL kwargs
        bridge = get_object_or_404(Bridge, pk=self.kwargs['bridge'])
        form.instance.bridge = bridge
        messages.success(self.request, f'Maintenance action for {bridge.name} scheduled successfully.')
        return super().form_valid(form)


# --- Maintenance Record Update View ---
class MaintenanceRecordUpdateView(MaintenanceRecordMixin, UpdateView):
    template_name = 'bridges/maintenance_record_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Maintenance record updated successfully.')
        return super().form_valid(form)


# --- Maintenance Record Delete View ---
class MaintenanceRecordDeleteView(MaintenanceRecordMixin, DeleteView):
    template_name = 'bridges/maintenance_record_confirm_delete.html'

    def get_success_url(self):
        # Override to ensure we get the bridge ID *before* the record is deleted
        bridge_pk = self.get_object().bridge.pk
        messages.success(self.request, 'Maintenance record deleted successfully.')
        return reverse('bridge_detail', kwargs={'pk': bridge_pk})

