from django.contrib import admin
from .models import CaffeineIntake
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import path
from django.db.models import Sum, Avg  # Import Sum and Avg

class CaffeineIntakeAdmin(admin.ModelAdmin):
    change_list_template = "admin/analytics_dashboard.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.analytics_view),
        ]
        return custom_urls + urls

    def analytics_view(self, request):
        # Aggregate data
        total_entries = CaffeineIntake.objects.count()
        total_caffeine_consumed = CaffeineIntake.objects.aggregate(Sum('amount'))['amount__sum']
        average_caffeine_per_entry = CaffeineIntake.objects.aggregate(Avg('amount'))['amount__avg']
        
        # Aggregate data per user
        user_caffeine_data = CaffeineIntake.objects.values('user__username').annotate(
            total_caffeine=Sum('amount'),
            avg_caffeine=Avg('amount')
        )
        
        context = {
            'total_entries': total_entries,
            'total_caffeine_consumed': total_caffeine_consumed,
            'average_caffeine_per_entry': average_caffeine_per_entry,
            'user_caffeine_data': user_caffeine_data,
        }
        
        html = render_to_string("admin/analytics_dashboard.html", context)
        return HttpResponse(html)

admin.site.register(CaffeineIntake, CaffeineIntakeAdmin)
