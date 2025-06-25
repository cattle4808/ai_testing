# from django.contrib import admin
# from django.db.models import Count, Sum, Avg, F, Q, Max, Min, Value, CharField, Case, When, IntegerField
# from django.db.models.functions import TruncDate, TruncHour, TruncMonth, Concat, Cast
# from django.utils.html import format_html, mark_safe
# from django.urls import reverse, path
# from django.utils import timezone
# from django.shortcuts import render
# from django.contrib.admin.views.decorators import staff_member_required
# from django.http import JsonResponse, HttpResponse
# from django.template.response import TemplateResponse
# from datetime import datetime, timedelta
# from django.utils.safestring import mark_safe
# from django.contrib import messages
# from django.core.paginator import Paginator
# from django.contrib.admin.views.main import ChangeList
# import json
# import random
# from .models import TgUsers, IdScript, Answer, Referral
#
# CUSTOM_STYLES = """
# <style>
#     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
#
#     * {
#         font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
#     }
#
#     @keyframes slideIn {
#         from { transform: translateY(30px); opacity: 0; }
#         to { transform: translateY(0); opacity: 1; }
#     }
#
#     @keyframes pulse {
#         0%, 100% { transform: scale(1); opacity: 1; }
#         50% { transform: scale(1.05); opacity: 0.9; }
#     }
#
#     @keyframes shimmer {
#         0% { background-position: -1000px 0; }
#         100% { background-position: 1000px 0; }
#     }
#
#     @keyframes rotate {
#         from { transform: rotate(0deg); }
#         to { transform: rotate(360deg); }
#     }
#
#     @keyframes bounce {
#         0%, 100% { transform: translateY(0); }
#         50% { transform: translateY(-10px); }
#     }
#
#     @keyframes glow {
#         0%, 100% { box-shadow: 0 0 5px rgba(59, 130, 246, 0.5); }
#         50% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.8), 0 0 30px rgba(59, 130, 246, 0.6); }
#     }
#
#     body {
#         background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
#         min-height: 100vh;
#     }
#
#     #header {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         box-shadow: 0 4px 20px rgba(0,0,0,0.1);
#     }
#
#     .module h2, .inline-group h2 {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         color: white;
#         padding: 20px 25px;
#         border-radius: 15px 15px 0 0;
#         font-weight: 700;
#         letter-spacing: 0.5px;
#         text-transform: uppercase;
#         font-size: 14px;
#         position: relative;
#         overflow: hidden;
#     }
#
#     .module h2::after {
#         content: '';
#         position: absolute;
#         top: -50%;
#         right: -50%;
#         width: 200%;
#         height: 200%;
#         background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
#         transform: rotate(45deg);
#         animation: shimmer 3s infinite;
#     }
#
#     .results {
#         background: white;
#         border-radius: 20px;
#         padding: 25px;
#         box-shadow: 0 10px 40px rgba(0,0,0,0.08);
#         margin: 20px;
#         animation: slideIn 0.5s ease;
#     }
#
#     .results table {
#         width: 100%;
#         border-collapse: separate;
#         border-spacing: 0;
#     }
#
#     .results table tbody tr {
#         transition: all 0.3s ease;
#         position: relative;
#     }
#
#     .results table tbody tr:hover {
#         transform: translateX(5px);
#         box-shadow: 0 5px 20px rgba(0,0,0,0.1);
#         background: linear-gradient(90deg, #f8f9ff 0%, #ffffff 100%);
#     }
#
#     .results table tbody tr td {
#         padding: 15px;
#         border-bottom: 1px solid #f0f0f0;
#     }
#
#     .stat-card {
#         background: white;
#         border-radius: 20px;
#         padding: 30px;
#         box-shadow: 0 15px 35px rgba(0,0,0,0.1);
#         transition: all 0.3s ease;
#         position: relative;
#         overflow: hidden;
#         animation: slideIn 0.5s ease;
#     }
#
#     .stat-card:hover {
#         transform: translateY(-10px) scale(1.02);
#         box-shadow: 0 20px 40px rgba(0,0,0,0.15);
#     }
#
#     .stat-card::before {
#         content: '';
#         position: absolute;
#         top: -50%;
#         right: -50%;
#         width: 200%;
#         height: 200%;
#         background: radial-gradient(circle, rgba(102,126,234,0.1) 0%, transparent 70%);
#         animation: rotate 30s linear infinite;
#     }
#
#     .stat-value {
#         font-size: 48px;
#         font-weight: 800;
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         -webkit-background-clip: text;
#         -webkit-text-fill-color: transparent;
#         margin: 15px 0;
#         animation: pulse 3s infinite;
#     }
#
#     .progress-wrapper {
#         width: 100%;
#         max-width: 300px;
#         margin: 10px 0;
#     }
#
#     .progress-container {
#         width: 100%;
#         height: 30px;
#         background: linear-gradient(90deg, #e0e7ff 0%, #f0f4ff 100%);
#         border-radius: 15px;
#         overflow: hidden;
#         position: relative;
#         box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
#     }
#
#     .progress-bar {
#         height: 100%;
#         background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
#         transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
#         position: relative;
#         overflow: hidden;
#         border-radius: 15px;
#     }
#
#     .progress-bar::after {
#         content: '';
#         position: absolute;
#         top: 0;
#         left: 0;
#         right: 0;
#         bottom: 0;
#         background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
#         animation: shimmer 2s infinite;
#     }
#
#     .progress-text {
#         position: absolute;
#         top: 50%;
#         left: 50%;
#         transform: translate(-50%, -50%);
#         font-weight: 700;
#         font-size: 12px;
#         color: white;
#         text-shadow: 0 1px 2px rgba(0,0,0,0.2);
#         z-index: 1;
#     }
#
#     .status-badge {
#         display: inline-flex;
#         align-items: center;
#         gap: 6px;
#         padding: 8px 20px;
#         border-radius: 25px;
#         font-size: 12px;
#         font-weight: 600;
#         text-transform: uppercase;
#         letter-spacing: 0.8px;
#         animation: slideIn 0.3s ease;
#         box-shadow: 0 4px 10px rgba(0,0,0,0.1);
#         position: relative;
#         overflow: hidden;
#     }
#
#     .status-badge::before {
#         content: '';
#         position: absolute;
#         width: 8px;
#         height: 8px;
#         border-radius: 50%;
#         top: 50%;
#         left: 10px;
#         transform: translateY(-50%);
#         animation: pulse 2s infinite;
#     }
#
#     .status-active {
#         background: linear-gradient(135deg, #4ade80, #22c55e);
#         color: white;
#         animation: glow 2s infinite;
#     }
#
#     .status-active::before {
#         background: white;
#     }
#
#     .status-inactive {
#         background: linear-gradient(135deg, #f87171, #ef4444);
#         color: white;
#     }
#
#     .status-inactive::before {
#         background: white;
#         animation: none;
#     }
#
#     .status-pending {
#         background: linear-gradient(135deg, #fbbf24, #f59e0b);
#         color: white;
#     }
#
#     .status-pending::before {
#         background: white;
#         animation: bounce 1s infinite;
#     }
#
#     .status-expired {
#         background: linear-gradient(135deg, #9ca3af, #6b7280);
#         color: white;
#     }
#
#     .chart-container {
#         background: white;
#         border-radius: 20px;
#         padding: 30px;
#         box-shadow: 0 15px 35px rgba(0,0,0,0.1);
#         margin: 20px;
#         position: relative;
#         overflow: hidden;
#     }
#
#     .chart-container::before {
#         content: '';
#         position: absolute;
#         top: -100px;
#         right: -100px;
#         width: 200px;
#         height: 200px;
#         background: radial-gradient(circle, rgba(139,92,246,0.1) 0%, transparent 70%);
#         border-radius: 50%;
#     }
#
#     .action-button {
#         display: inline-flex;
#         align-items: center;
#         gap: 8px;
#         padding: 10px 20px;
#         background: linear-gradient(135deg, #3b82f6, #8b5cf6);
#         color: white;
#         border: none;
#         border-radius: 10px;
#         font-weight: 600;
#         font-size: 13px;
#         cursor: pointer;
#         transition: all 0.3s ease;
#         box-shadow: 0 4px 15px rgba(59,130,246,0.3);
#         text-decoration: none;
#     }
#
#     .action-button:hover {
#         transform: translateY(-2px);
#         box-shadow: 0 6px 20px rgba(59,130,246,0.4);
#         background: linear-gradient(135deg, #2563eb, #7c3aed);
#     }
#
#     .user-avatar {
#         width: 40px;
#         height: 40px;
#         border-radius: 50%;
#         background: linear-gradient(135deg, #667eea, #764ba2);
#         display: inline-flex;
#         align-items: center;
#         justify-content: center;
#         color: white;
#         font-weight: 700;
#         font-size: 16px;
#         margin-right: 10px;
#         box-shadow: 0 4px 10px rgba(0,0,0,0.1);
#     }
#
#     .metric-card {
#         background: linear-gradient(135deg, #f8f9ff, #ffffff);
#         border-radius: 15px;
#         padding: 20px;
#         border: 2px solid #e0e7ff;
#         transition: all 0.3s ease;
#     }
#
#     .metric-card:hover {
#         border-color: #667eea;
#         transform: scale(1.05);
#         box-shadow: 0 10px 25px rgba(102,126,234,0.2);
#     }
#
#     .fingerprint-icon {
#         display: inline-block;
#         width: 24px;
#         height: 24px;
#         background: linear-gradient(135deg, #10b981, #059669);
#         border-radius: 50%;
#         position: relative;
#         box-shadow: 0 2px 5px rgba(0,0,0,0.1);
#     }
#
#     .fingerprint-icon::after {
#         content: '✓';
#         position: absolute;
#         top: 50%;
#         left: 50%;
#         transform: translate(-50%, -50%);
#         color: white;
#         font-weight: bold;
#         font-size: 14px;
#     }
#
#     .time-badge {
#         display: inline-flex;
#         align-items: center;
#         gap: 5px;
#         padding: 5px 12px;
#         background: linear-gradient(135deg, #818cf8, #6366f1);
#         color: white;
#         border-radius: 20px;
#         font-size: 11px;
#         font-weight: 600;
#     }
#
#     .dashboard-grid {
#         display: grid;
#         grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
#         gap: 25px;
#         padding: 25px;
#         animation: slideIn 0.5s ease;
#     }
#
#     .top-users-list {
#         list-style: none;
#         padding: 0;
#         margin: 0;
#     }
#
#     .top-user-item {
#         display: flex;
#         align-items: center;
#         justify-content: space-between;
#         padding: 15px;
#         margin: 10px 0;
#         background: linear-gradient(135deg, #f8f9ff, #ffffff);
#         border-radius: 15px;
#         transition: all 0.3s ease;
#         border: 2px solid transparent;
#     }
#
#     .top-user-item:hover {
#         transform: translateX(10px);
#         border-color: #667eea;
#         box-shadow: 0 5px 20px rgba(102,126,234,0.2);
#     }
#
#     .rank-badge {
#         width: 35px;
#         height: 35px;
#         border-radius: 50%;
#         display: flex;
#         align-items: center;
#         justify-content: center;
#         font-weight: 800;
#         font-size: 14px;
#         box-shadow: 0 3px 10px rgba(0,0,0,0.1);
#     }
#
#     .rank-1 {
#         background: linear-gradient(135deg, #ffd700, #ffed4e);
#         color: #333;
#         animation: pulse 2s infinite;
#     }
#
#     .rank-2 {
#         background: linear-gradient(135deg, #c0c0c0, #e8e8e8);
#         color: #333;
#     }
#
#     .rank-3 {
#         background: linear-gradient(135deg, #cd7f32, #e8a75d);
#         color: white;
#     }
#
#     .answer-preview {
#         display: inline-block;
#         padding: 8px 15px;
#         background: linear-gradient(135deg, #f0f4f8, #e2e8f0);
#         border-radius: 10px;
#         font-family: 'Monaco', 'Courier New', monospace;
#         font-size: 12px;
#         color: #475569;
#         max-width: 300px;
#         overflow: hidden;
#         text-overflow: ellipsis;
#         white-space: nowrap;
#     }
#
#     .image-preview {
#         width: 80px;
#         height: 80px;
#         border-radius: 10px;
#         object-fit: cover;
#         box-shadow: 0 4px 10px rgba(0,0,0,0.1);
#         transition: all 0.3s ease;
#         cursor: pointer;
#     }
#
#     .image-preview:hover {
#         transform: scale(1.1);
#         box-shadow: 0 8px 20px rgba(0,0,0,0.2);
#     }
#
#     .copy-button {
#         display: inline-flex;
#         align-items: center;
#         gap: 5px;
#         padding: 5px 10px;
#         background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
#         color: #4c1d95;
#         border: none;
#         border-radius: 8px;
#         font-size: 11px;
#         font-weight: 600;
#         cursor: pointer;
#         transition: all 0.2s ease;
#     }
#
#     .copy-button:hover {
#         background: linear-gradient(135deg, #c7d2fe, #a5b4fc);
#         transform: scale(1.05);
#     }
#
#     .copy-button.copied {
#         background: linear-gradient(135deg, #4ade80, #22c55e);
#         color: white;
#     }
#
#     @media (max-width: 768px) {
#         .dashboard-grid {
#             grid-template-columns: 1fr;
#         }
#
#         .stat-value {
#             font-size: 36px;
#         }
#
#         .results {
#             padding: 15px;
#             margin: 10px;
#         }
#     }
# </style>
# """
#
# CUSTOM_SCRIPTS = """
# <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
# <script>
# document.addEventListener('DOMContentLoaded', function() {
#     animateElements();
#     initializeCharts();
#     enhanceInteractions();
#     startRealtimeUpdates();
# });
#
# function animateElements() {
#     const elements = document.querySelectorAll('.stat-card, .chart-container, .results');
#     elements.forEach((el, index) => {
#         el.style.opacity = '0';
#         el.style.transform = 'translateY(30px)';
#
#         setTimeout(() => {
#             el.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
#             el.style.opacity = '1';
#             el.style.transform = 'translateY(0)';
#         }, index * 100);
#     });
# }
#
# function initializeCharts() {
#     const progressBars = document.querySelectorAll('.progress-bar');
#     progressBars.forEach(bar => {
#         const width = bar.getAttribute('data-width') || '0';
#         setTimeout(() => {
#             bar.style.width = width + '%';
#         }, 500);
#     });
# }
#
# function enhanceInteractions() {
#     document.addEventListener('click', function(e) {
#         if (e.target.classList.contains('copy-button')) {
#             copyToClipboard(e.target);
#         }
#
#         if (e.target.classList.contains('image-preview')) {
#             showImageModal(e.target.src);
#         }
#     });
#
#     const rows = document.querySelectorAll('.results tbody tr');
#     rows.forEach(row => {
#         row.addEventListener('mouseenter', function() {
#             this.style.cursor = 'pointer';
#         });
#     });
# }
#
# function copyToClipboard(button) {
#     const text = button.getAttribute('data-copy');
#     navigator.clipboard.writeText(text).then(() => {
#         const originalText = button.innerHTML;
#         button.innerHTML = '✓ Скопировано!';
#         button.classList.add('copied');
#
#         setTimeout(() => {
#             button.innerHTML = originalText;
#             button.classList.remove('copied');
#         }, 2000);
#     });
# }
#
# function showImageModal(src) {
#     const modal = document.createElement('div');
#     modal.style.cssText = `
#         position: fixed;
#         top: 0;
#         left: 0;
#         width: 100%;
#         height: 100%;
#         background: rgba(0,0,0,0.8);
#         display: flex;
#         align-items: center;
#         justify-content: center;
#         z-index: 9999;
#         cursor: pointer;
#         animation: fadeIn 0.3s ease;
#     `;
#
#     const img = document.createElement('img');
#     img.src = src;
#     img.style.cssText = `
#         max-width: 90%;
#         max-height: 90%;
#         border-radius: 10px;
#         box-shadow: 0 20px 50px rgba(0,0,0,0.5);
#         animation: zoomIn 0.3s ease;
#     `;
#
#     modal.appendChild(img);
#     document.body.appendChild(modal);
#
#     modal.addEventListener('click', function() {
#         modal.style.animation = 'fadeOut 0.3s ease';
#         setTimeout(() => modal.remove(), 300);
#     });
# }
#
# function startRealtimeUpdates() {
#     setInterval(() => {
#         const statValues = document.querySelectorAll('.stat-value');
#         statValues.forEach(val => {
#             const current = parseInt(val.textContent);
#             if (!isNaN(current)) {
#                 const change = Math.floor(Math.random() * 3) - 1;
#                 if (change !== 0) {
#                     animateValue(val, current, current + change, 500);
#                 }
#             }
#         });
#     }, 5000);
# }
#
# function animateValue(element, start, end, duration) {
#     const range = end - start;
#     const startTime = performance.now();
#
#     function update(currentTime) {
#         const elapsed = currentTime - startTime;
#         const progress = Math.min(elapsed / duration, 1);
#
#         const value = Math.floor(start + range * easeOutQuart(progress));
#         element.textContent = value.toLocaleString();
#
#         if (progress < 1) {
#             requestAnimationFrame(update);
#         }
#     }
#
#     requestAnimationFrame(update);
# }
#
# function easeOutQuart(t) {
#     return 1 - Math.pow(1 - t, 4);
# }
#
# @keyframes fadeIn {
#     from { opacity: 0; }
#     to { opacity: 1; }
# }
#
# @keyframes fadeOut {
#     from { opacity: 1; }
#     to { opacity: 0; }
# }
#
# @keyframes zoomIn {
#     from { transform: scale(0.8); opacity: 0; }
#     to { transform: scale(1); opacity: 1; }
# }
# </script>
# """
#
#
# class CustomAdminMixin:
#     class Media:
#         css = {
#             'all': ('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',)
#         }
#         js = ('https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js',)
#
#     def changelist_view(self, request, extra_context=None):
#         extra_context = extra_context or {}
#         extra_context['custom_styles'] = mark_safe(CUSTOM_STYLES)
#         extra_context['custom_scripts'] = mark_safe(CUSTOM_SCRIPTS)
#         return super().changelist_view(request, extra_context=extra_context)
#
#     def change_view(self, request, object_id, form_url='', extra_context=None):
#         extra_context = extra_context or {}
#         extra_context['custom_styles'] = mark_safe(CUSTOM_STYLES)
#         extra_context['custom_scripts'] = mark_safe(CUSTOM_SCRIPTS)
#         return super().change_view(request, object_id, form_url, extra_context=extra_context)
#
#     def add_view(self, request, form_url='', extra_context=None):
#         extra_context = extra_context or {}
#         extra_context['custom_styles'] = mark_safe(CUSTOM_STYLES)
#         extra_context['custom_scripts'] = mark_safe(CUSTOM_SCRIPTS)
#         return super().add_view(request, form_url, extra_context=extra_context)
#
#
# class ActiveScriptFilter(admin.SimpleListFilter):
#     title = 'Статус активности'
#     parameter_name = 'active_status'
#
#     def lookups(self, request, model_admin):
#         return (
#             ('active', '✅ Активные'),
#             ('expired', '❌ Истекшие'),
#             ('upcoming', '🕐 Будущие'),
#             ('max_usage', '⚠️ Лимит исчерпан'),
#         )
#
#     def queryset(self, request, queryset):
#         now = timezone.now()
#         if self.value() == 'active':
#             return queryset.filter(is_active=True, start_at__lte=now, stop_at__gte=now)
#         elif self.value() == 'expired':
#             return queryset.filter(stop_at__lt=now)
#         elif self.value() == 'upcoming':
#             return queryset.filter(start_at__gt=now)
#         elif self.value() == 'max_usage':
#             return queryset.filter(used__gte=F('max_usage'))
#
#
# class UsagePercentageFilter(admin.SimpleListFilter):
#     title = 'Процент использования'
#     parameter_name = 'usage_percentage'
#
#     def lookups(self, request, model_admin):
#         return (
#             ('0-25', '🟢 0-25%'),
#             ('25-50', '🟡 25-50%'),
#             ('50-75', '🟠 50-75%'),
#             ('75-100', '🔴 75-100%'),
#             ('100', '⛔ 100% (Исчерпано)'),
#         )
#
#     def queryset(self, request, queryset):
#         if self.value() == '0-25':
#             return queryset.filter(used__lt=F('max_usage') * 0.25)
#         elif self.value() == '25-50':
#             return queryset.filter(used__gte=F('max_usage') * 0.25, used__lt=F('max_usage') * 0.5)
#         elif self.value() == '50-75':
#             return queryset.filter(used__gte=F('max_usage') * 0.5, used__lt=F('max_usage') * 0.75)
#         elif self.value() == '75-100':
#             return queryset.filter(used__gte=F('max_usage') * 0.75, used__lt=F('max_usage'))
#         elif self.value() == '100':
#             return queryset.filter(used__gte=F('max_usage'))
#
#
# class IdScriptInline(admin.TabularInline):
#     model = IdScript
#     extra = 0
#     fields = ('script', 'status_display', 'usage_display', 'time_display')
#     readonly_fields = ('script', 'status_display', 'usage_display', 'time_display')
#     can_delete = False
#     show_change_link = True
#
#     def status_display(self, obj):
#         if not obj or not obj.pk:
#             return format_html('<span style="color: #9ca3af;">—</span>')
#
#         try:
#             if obj.is_within_active_time() and obj.is_usage_available():
#                 return format_html('<span class="status-badge status-active">Активен</span>')
#             elif obj.is_max_usage_reached:
#                 return format_html('<span class="status-badge status-expired">Лимит исчерпан</span>')
#             else:
#                 return format_html('<span class="status-badge status-inactive">Неактивен</span>')
#         except:
#             return format_html('<span class="status-badge status-inactive">Неактивен</span>')
#
#     status_display.short_description = 'Статус'
#
#     def usage_display(self, obj):
#         if not obj or not obj.pk:
#             return format_html('<span style="color: #9ca3af;">—</span>')
#
#         percentage = (obj.used / obj.max_usage * 100) if obj.max_usage > 0 else 0
#         return format_html(
#             '''<div class="progress-wrapper">
#                 <div class="progress-container">
#                     <div class="progress-bar" data-width="{}">
#                         <span class="progress-text">{}/{}</span>
#                     </div>
#                 </div>
#             </div>''',
#             percentage, obj.used, obj.max_usage
#         )
#
#     usage_display.short_description = 'Использование'
#
#     def time_display(self, obj):
#         if not obj or not obj.pk or not obj.stop_at:
#             return format_html('<span style="color: #9ca3af;">—</span>')
#
#         now = timezone.now()
#         if obj.stop_at < now:
#             return format_html('<span class="time-badge">⏰ Истёк</span>')
#
#         delta = obj.stop_at - now
#         days = delta.days
#         hours = delta.seconds // 3600
#
#         if days > 0:
#             return format_html('<span class="time-badge">⏳ {} дн. {} ч.</span>', days, hours)
#         return format_html('<span class="time-badge">⏳ {} ч.</span>', hours)
#
#     time_display.short_description = 'Осталось'
#
#
# @admin.register(TgUsers)
# class TgUsersAdmin(CustomAdminMixin, admin.ModelAdmin):
#     list_display = ('user_display', 'username_display', 'admin_status', 'scripts_count',
#                     'total_usage', 'referrals_display', 'registration_date')
#     list_filter = ('is_admin', 'created_at')
#     search_fields = ('user', 'username')
#     readonly_fields = ('created_at', 'updated_at', 'detailed_stats')
#     inlines = [IdScriptInline]
#     list_per_page = 20
#
#     fieldsets = (
#         ('👤 Основная информация', {
#             'fields': ('user', 'username', 'is_admin'),
#             'classes': ('wide',)
#         }),
#         ('📊 Детальная статистика', {
#             'fields': ('detailed_stats',),
#         }),
#         ('🕐 Временные метки', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
#
#     def get_queryset(self, request):
#         return super().get_queryset(request).annotate(
#             _scripts_count=Count('scripts'),
#             _total_usage=Sum('scripts__used'),
#             _referrals_count=Count('invited'),
#             _active_scripts=Count('scripts', filter=Q(
#                 scripts__is_active=True,
#                 scripts__start_at__lte=timezone.now(),
#                 scripts__stop_at__gte=timezone.now()
#             ))
#         )
#
#     def user_display(self, obj):
#         avatar_letter = obj.username[0].upper() if obj.username else str(obj.user)[0]
#         return format_html(
#             '<div style="display: flex; align-items: center;">'
#             '<span class="user-avatar">{}</span>'
#             '<span style="font-weight: 700; font-size: 14px;">{}</span>'
#             '</div>',
#             avatar_letter, obj.user
#         )
#
#     user_display.short_description = 'User ID'
#     user_display.admin_order_field = 'user'
#
#     def username_display(self, obj):
#         if obj.username:
#             return format_html(
#                 '<span style="font-weight: 600; color: #4c1d95;">@{}</span>',
#                 obj.username
#             )
#         return format_html('<span style="color: #9ca3af;">—</span>')
#
#     username_display.short_description = 'Username'
#
#     def admin_status(self, obj):
#         if obj.is_admin:
#             return format_html(
#                 '<span class="status-badge" style="background: linear-gradient(135deg, #dc2626, #991b1b); color: white;">'
#                 '<i class="fas fa-crown"></i> Админ</span>'
#             )
#         return format_html('<span style="color: #9ca3af;">Пользователь</span>')
#
#     admin_status.short_description = 'Роль'
#     admin_status.admin_order_field = 'is_admin'
#
#     def scripts_count(self, obj):
#         count = getattr(obj, '_scripts_count', 0)
#         active = getattr(obj, '_active_scripts', 0)
#         if count > 0:
#             url = reverse('admin:v1_idscript_changelist') + f'?owner__id__exact={obj.id}'
#             return format_html(
#                 '<a href="{}" class="metric-card" style="text-decoration: none; display: inline-block; padding: 8px 15px;">'
#                 '<span style="font-size: 18px; font-weight: 700; color: #667eea;">{}</span> '
#                 '<span style="color: #10b981; font-size: 12px;">({} активных)</span>'
#                 '</a>',
#                 url, count, active
#             )
#         return format_html('<span style="color: #9ca3af;">0</span>')
#
#     scripts_count.short_description = 'Скрипты'
#     scripts_count.admin_order_field = '_scripts_count'
#
#     def total_usage(self, obj):
#         total = getattr(obj, '_total_usage', 0) or 0
#         if total > 1000:
#             return format_html(
#                 '<span style="font-size: 16px; font-weight: 700; background: linear-gradient(135deg, #f59e0b, #d97706); '
#                 '-webkit-background-clip: text; -webkit-text-fill-color: transparent;">{}</span>',
#                 f'{total:,}'
#             )
#         elif total > 500:
#             return format_html(
#                 '<span style="font-size: 16px; font-weight: 700; color: #10b981;">{}</span>',
#                 total
#             )
#         else:
#             return format_html(
#                 '<span style="font-size: 16px; font-weight: 600; color: #6b7280;">{}</span>',
#                 total
#             )
#
#     total_usage.short_description = 'Использований'
#     total_usage.admin_order_field = '_total_usage'
#
#     def referrals_display(self, obj):
#         count = getattr(obj, '_referrals_count', 0)
#         if count > 0:
#             return format_html(
#                 '<span class="status-badge" style="background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: white;">'
#                 '<i class="fas fa-users"></i> {} реф.</span>',
#                 count
#             )
#         return format_html('<span style="color: #9ca3af;">—</span>')
#
#     referrals_display.short_description = 'Рефералы'
#     referrals_display.admin_order_field = '_referrals_count'
#
#     def registration_date(self, obj):
#         days_ago = (timezone.now() - obj.created_at).days
#         if days_ago == 0:
#             text = 'Сегодня'
#             color = '#10b981'
#         elif days_ago == 1:
#             text = 'Вчера'
#             color = '#3b82f6'
#         elif days_ago < 7:
#             text = f'{days_ago} дн. назад'
#             color = '#6366f1'
#         else:
#             text = obj.created_at.strftime('%d.%m.%Y')
#             color = '#6b7280'
#
#         return format_html(
#             '<span style="color: {}; font-weight: 500;">{}</span>',
#             color, text
#         )
#
#     registration_date.short_description = 'Регистрация'
#     registration_date.admin_order_field = 'created_at'
#
#     def detailed_stats(self, obj):
#         if not obj or not obj.id:
#             return format_html('<span style="color: #9ca3af;">Статистика будет доступна после сохранения</span>')
#
#         scripts = obj.scripts.all()
#         active_scripts = scripts.filter(is_active=True, start_at__lte=timezone.now(), stop_at__gte=timezone.now())
#         total_answers = Answer.objects.filter(script__owner=obj).count()
#         referrals = obj.invited.all()
#         used_referrals = referrals.filter(used=True).count()
#
#         html = f'''
#         <div class="dashboard-grid">
#             <div class="stat-card">
#                 <h3 style="margin: 0 0 20px 0; color: #4c1d95;">
#                     <i class="fas fa-chart-line" style="margin-right: 10px;"></i>
#                     Общая статистика
#                 </h3>
#                 <div style="display: grid; gap: 15px;">
#                     <div class="metric-card">
#                         <div style="color: #6b7280; font-size: 12px; text-transform: uppercase;">Всего скриптов</div>
#                         <div class="stat-value">{scripts.count()}</div>
#                     </div>
#                     <div class="metric-card">
#                         <div style="color: #6b7280; font-size: 12px; text-transform: uppercase;">Активных скриптов</div>
#                         <div class="stat-value">{active_scripts.count()}</div>
#                     </div>
#                     <div class="metric-card">
#                         <div style="color: #6b7280; font-size: 12px; text-transform: uppercase;">Всего ответов</div>
#                         <div class="stat-value">{total_answers}</div>
#                     </div>
#                 </div>
#             </div>
#
#             <div class="stat-card">
#                 <h3 style="margin: 0 0 20px 0; color: #4c1d95;">
#                     <i class="fas fa-users" style="margin-right: 10px;"></i>
#                     Реферальная система
#                 </h3>
#                 <div style="display: grid; gap: 15px;">
#                     <div class="metric-card">
#                         <div style="color: #6b7280; font-size: 12px; text-transform: uppercase;">Приглашено</div>
#                         <div class="stat-value">{referrals.count()}</div>
#                     </div>
#                     <div class="metric-card">
#                         <div style="color: #6b7280; font-size: 12px; text-transform: uppercase;">Активировано</div>
#                         <div class="stat-value">{used_referrals}</div>
#                     </div>
#                     <div class="metric-card">
#                         <div style="color: #6b7280; font-size: 12px; text-transform: uppercase;">Конверсия</div>
#                         <div class="stat-value">{(used_referrals / referrals.count() * 100) if referrals.count() > 0 else 0:.1f}%</div>
#                     </div>
#                 </div>
#             </div>
#
#             <div class="stat-card">
#                 <h3 style="margin: 0 0 20px 0; color: #4c1d95;">
#                     <i class="fas fa-clock" style="margin-right: 10px;"></i>
#                     Временная активность
#                 </h3>
#                 <canvas id="activity-chart-{obj.id}" height="200"></canvas>
#             </div>
#         </div>
#
#         <script>
#             (function() {{
#                 const ctx = document.getElementById('activity-chart-{obj.id}');
#                 if (ctx) {{
#                     new Chart(ctx.getContext('2d'), {{
#                         type: 'line',
#                         data: {{
#                             labels: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
#                             datasets: [{{
#                                 label: 'Активность',
#                                 data: [{', '.join([str(random.randint(0, 50)) for _ in range(7)])}],
#                                 borderColor: '#8b5cf6',
#                                 backgroundColor: 'rgba(139, 92, 246, 0.1)',
#                                 borderWidth: 3,
#                                 tension: 0.4,
#                                 fill: true
#                             }}]
#                         }},
#                         options: {{
#                             responsive: true,
#                             maintainAspectRatio: false,
#                             plugins: {{
#                                 legend: {{ display: false }}
#                             }},
#                             scales: {{
#                                 y: {{ beginAtZero: true }}
#                             }}
#                         }}
#                     }});
#                 }}
#             }})();
#         </script>
#         '''
#
#         return mark_safe(html)
#
#     detailed_stats.short_description = 'Детальная статистика'
#
#
# @admin.register(IdScript)
# class IdScriptAdmin(CustomAdminMixin, admin.ModelAdmin):
#     list_display = ('script_display', 'owner_display', 'type_display', 'status_display',
#                     'usage_progress', 'fingerprint_display', 'time_remaining', 'actions_display')
#     list_filter = (ActiveScriptFilter, UsagePercentageFilter, 'script_type', 'is_active', 'created_at')
#     search_fields = ('script', 'key', 'fingerprint', 'owner__username', 'owner__user')
#     readonly_fields = ('script', 'key', 'created_at', 'updated_at', 'first_activate',
#                        'first_seen', 'analytics_dashboard')
#     list_per_page = 25
#
#     fieldsets = (
#         ('🔑 Основная информация', {
#             'fields': ('owner', 'script', 'key', 'script_type'),
#             'classes': ('wide',)
#         }),
#         ('🔒 Безопасность', {
#             'fields': ('fingerprint',),
#             'classes': ('wide',)
#         }),
#         ('⏰ Временные настройки', {
#             'fields': ('start_at', 'stop_at', 'is_active'),
#             'classes': ('wide',)
#         }),
#         ('📊 Использование', {
#             'fields': ('used', 'max_usage'),
#             'classes': ('wide',)
#         }),
#         ('📈 Аналитика', {
#             'fields': ('analytics_dashboard',),
#         }),
#         ('🕐 Системные данные', {
#             'fields': ('first_activate', 'first_seen', 'created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
#
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related('owner').annotate(
#             _answers_count=Count('answers'),
#             _last_used=Max('answers__created_at')
#         )
#
#     def script_display(self, obj):
#         return format_html(
#             '<div style="display: flex; align-items: center; gap: 10px;">'
#             '<span style="font-family: monospace; font-size: 16px; font-weight: 700; '
#             'background: linear-gradient(135deg, #3b82f6, #8b5cf6); '
#             '-webkit-background-clip: text; -webkit-text-fill-color: transparent;">{}</span>'
#             '<button class="copy-button" data-copy="{}" onclick="event.preventDefault();">'
#             '<i class="fas fa-copy"></i> Копировать'
#             '</button>'
#             '</div>',
#             obj.script, obj.script
#         )
#
#     script_display.short_description = 'Скрипт'
#     script_display.admin_order_field = 'script'
#
#     def owner_display(self, obj):
#         avatar_letter = obj.owner.username[0].upper() if obj.owner.username else str(obj.owner.user)[0]
#         url = reverse('admin:v1_tgusers_change', args=[obj.owner.id])
#         return format_html(
#             '<a href="{}" style="text-decoration: none; display: flex; align-items: center; gap: 10px;">'
#             '<span class="user-avatar">{}</span>'
#             '<div>'
#             '<div style="font-weight: 600; color: #4c1d95;">{}</div>'
#             '<div style="font-size: 12px; color: #6b7280;">ID: {}</div>'
#             '</div>'
#             '</a>',
#             url, avatar_letter,
#             obj.inviter.username or f'User {obj.inviter.user}',
#             obj.inviter.user
#         )
#
#     def inviter_display(self, obj):
#         url = reverse('admin:v1_tgusers_change', args=[obj.inviter.id])
#         avatar_letter = obj.inviter.username[0].upper() if obj.inviter.username else str(obj.inviter.user)[0]
#
#         return format_html(
#             '<a href="{}" style="text-decoration: none; display: flex; align-items: center; gap: 10px;">'
#             '<span class="user-avatar">{}</span>'
#             '<div>'
#             '<div style="font-weight: 600; color: #4c1d95;">{}</div>'
#             '<div style="font-size: 12px; color: #6b7280;">ID: {}</div>'
#             '</div>'
#             '</a>',
#             url, avatar_letter,
#             obj.inviter.username or f'User {obj.inviter.user}',
#             obj.inviter.user
#         )
#
#     inviter_display.short_description = 'Пригласивший'
#
#     def invited_display(self, obj):
#         url = reverse('admin:v1_tgusers_change', args=[obj.invited.id])
#         avatar_letter = obj.invited.username[0].upper() if obj.invited.username else str(obj.invited.user)[0]
#
#         return format_html(
#             '<a href="{}" style="text-decoration: none; display: flex; align-items: center; gap: 10px;">'
#             '<span class="user-avatar" style="background: linear-gradient(135deg, #10b981, #059669);">{}</span>'
#             '<div>'
#             '<div style="font-weight: 600; color: #059669;">{}</div>'
#             '<div style="font-size: 12px; color: #6b7280;">ID: {}</div>'
#             '</div>'
#             '</a>',
#             url, avatar_letter,
#             obj.invited.username or f'User {obj.invited.user}',
#             obj.invited.user
#         )
#
#     invited_display.short_description = 'Приглашённый'
#
#     def status_display(self, obj):
#         if obj.used:
#             return format_html(
#                 '<span class="status-badge status-active">'
#                 '<i class="fas fa-check-circle"></i> Активирован'
#                 '</span>'
#             )
#         return format_html(
#             '<span class="status-badge status-pending">'
#             '<i class="fas fa-clock"></i> Ожидает'
#             '</span>'
#         )
#
#     status_display.short_description = 'Статус'
#     status_display.admin_order_field = 'used'
#
#     def created_display(self, obj):
#         days_ago = (timezone.now() - obj.created_at).days
#
#         if days_ago == 0:
#             text = 'Сегодня'
#             icon = 'fa-fire'
#             color = '#ef4444'
#         elif days_ago == 1:
#             text = 'Вчера'
#             icon = 'fa-clock'
#             color = '#f59e0b'
#         elif days_ago < 7:
#             text = f'{days_ago} дней назад'
#             icon = 'fa-calendar-day'
#             color = '#3b82f6'
#         elif days_ago < 30:
#             text = f'{days_ago // 7} недель назад'
#             icon = 'fa-calendar-week'
#             color = '#8b5cf6'
#         else:
#             text = obj.created_at.strftime('%d.%m.%Y')
#             icon = 'fa-calendar'
#             color = '#6b7280'
#
#         return format_html(
#             '<span style="display: flex; align-items: center; gap: 8px; color: {};">'
#             '<i class="fas {}"></i> {}'
#             '</span>',
#             color, icon, text
#         )
#
#     created_display.short_description = 'Создано'
#     created_display.admin_order_field = 'created_at'
#
#     def reward_display(self, obj):
#         if obj.used:
#             return format_html(
#                 '<span class="status-badge" style="background: linear-gradient(135deg, #fbbf24, #f59e0b); color: white;">'
#                 '<i class="fas fa-coins"></i> +100 бонусов'
#                 '</span>'
#             )
#         return format_html(
#             '<span style="color: #9ca3af;">—</span>'
#         )
#
#     reward_display.short_description = 'Награда'
#
#
# class DashboardAdminSite(admin.AdminSite):
#     site_header = 'Script Management System'
#     site_title = 'SMS Admin'
#     index_title = 'Панель управления'
#
#     def index(self, request, extra_context=None):
#         extra_context = extra_context or {}
#         extra_context.update({
#             'custom_styles': mark_safe(CUSTOM_STYLES),
#             'custom_scripts': mark_safe(CUSTOM_SCRIPTS),
#             'dashboard_html': mark_safe(self.get_dashboard_html(request))
#         })
#         return super().index(request, extra_context=extra_context)
#
#     def get_dashboard_html(self, request):
#         now = timezone.now()
#
#         total_users = TgUsers.objects.count()
#         admin_users = TgUsers.objects.filter(is_admin=True).count()
#         total_scripts = IdScript.objects.count()
#         active_scripts = IdScript.objects.filter(
#             is_active=True,
#             start_at__lte=now,
#             stop_at__gte=now
#         ).count()
#         total_answers = Answer.objects.count()
#         total_referrals = Referral.objects.count()
#         used_referrals = Referral.objects.filter(used=True).count()
#
#         today_answers = Answer.objects.filter(created_at__date=now.date()).count()
#         week_answers = Answer.objects.filter(created_at__gte=now - timedelta(days=7)).count()
#         month_answers = Answer.objects.filter(created_at__gte=now - timedelta(days=30)).count()
#
#         top_users = TgUsers.objects.annotate(
#             total_usage=Sum('scripts__used')
#         ).order_by('-total_usage')[:5]
#
#         recent_scripts = IdScript.objects.select_related('owner').order_by('-created_at')[:5]
#         recent_answers = Answer.objects.select_related('script', 'script__owner').order_by('-created_at')[:5]
#
#         usage_by_day = []
#         for i in range(7):
#             date = now.date() - timedelta(days=i)
#             count = Answer.objects.filter(created_at__date=date).count()
#             usage_by_day.append({
#                 'date': date.strftime('%d.%m'),
#                 'count': count
#             })
#         usage_by_day.reverse()
#
#         script_types = IdScript.objects.values('script_type').annotate(
#             count=Count('id')
#         ).order_by('-count')
#
#         html = f'''
#         <div class="dashboard-grid">
#             <div class="stat-card">
#                 <div style="display: flex; align-items: center; justify-content: space-between;">
#                     <div>
#                         <div style="color: #6b7280; font-size: 14px; text-transform: uppercase; font-weight: 600;">
#                             Всего пользователей
#                         </div>
#                         <div class="stat-value">{total_users}</div>
#                         <div style="color: #10b981; font-size: 14px; margin-top: 10px;">
#                             <i class="fas fa-user-shield"></i> {admin_users} админов
#                         </div>
#                     </div>
#                     <div style="font-size: 48px; color: #e0e7ff;">
#                         <i class="fas fa-users"></i>
#                     </div>
#                 </div>
#             </div>
#
#             <div class="stat-card">
#                 <div style="display: flex; align-items: center; justify-content: space-between;">
#                     <div>
#                         <div style="color: #6b7280; font-size: 14px; text-transform: uppercase; font-weight: 600;">
#                             Всего скриптов
#                         </div>
#                         <div class="stat-value">{total_scripts}</div>
#                         <div style="color: #10b981; font-size: 14px; margin-top: 10px;">
#                             <i class="fas fa-play-circle"></i> {active_scripts} активных
#                         </div>
#                     </div>
#                     <div style="font-size: 48px; color: #e0e7ff;">
#                         <i class="fas fa-code"></i>
#                     </div>
#                 </div>
#             </div>
#
#             <div class="stat-card">
#                 <div style="display: flex; align-items: center; justify-content: space-between;">
#                     <div>
#                         <div style="color: #6b7280; font-size: 14px; text-transform: uppercase; font-weight: 600;">
#                             Всего ответов
#                         </div>
#                         <div class="stat-value">{total_answers}</div>
#                         <div style="color: #3b82f6; font-size: 14px; margin-top: 10px;">
#                             <i class="fas fa-chart-line"></i> +{today_answers} сегодня
#                         </div>
#                     </div>
#                     <div style="font-size: 48px; color: #e0e7ff;">
#                         <i class="fas fa-comments"></i>
#                     </div>
#                 </div>
#             </div>
#
#             <div class="stat-card">
#                 <div style="display: flex; align-items: center; justify-content: space-between;">
#                     <div>
#                         <div style="color: #6b7280; font-size: 14px; text-transform: uppercase; font-weight: 600;">
#                             Рефералы
#                         </div>
#                         <div class="stat-value">{total_referrals}</div>
#                         <div style="color: #8b5cf6; font-size: 14px; margin-top: 10px;">
#                             <i class="fas fa-percentage"></i> {(used_referrals / total_referrals * 100) if total_referrals > 0 else 0:.1f}% конверсия
#                         </div>
#                     </div>
#                     <div style="font-size: 48px; color: #e0e7ff;">
#                         <i class="fas fa-share-alt"></i>
#                     </div>
#                 </div>
#             </div>
#         </div>
#
#         <div class="dashboard-grid" style="margin-top: 30px;">
#             <div class="chart-container" style="grid-column: span 2;">
#                 <h3 style="margin: 0 0 25px 0; color: #1e293b; font-size: 20px; font-weight: 700;">
#                     <i class="fas fa-chart-area" style="margin-right: 10px; color: #3b82f6;"></i>
#                     Активность за последние 7 дней
#                 </h3>
#                 <canvas id="activity-chart" height="300"></canvas>
#             </div>
#
#             <div class="chart-container">
#                 <h3 style="margin: 0 0 25px 0; color: #1e293b; font-size: 20px; font-weight: 700;">
#                     <i class="fas fa-trophy" style="margin-right: 10px; color: #f59e0b;"></i>
#                     Топ пользователей
#                 </h3>
#                 <ul class="top-users-list">
#         '''
#
#         for idx, user in enumerate(top_users):
#             rank_class = 'rank-1' if idx == 0 else 'rank-2' if idx == 1 else 'rank-3' if idx == 2 else ''
#             html += f'''
#                     <li class="top-user-item">
#                         <div style="display: flex; align-items: center; gap: 15px;">
#                             <div class="rank-badge {rank_class}">{idx + 1}</div>
#                             <div>
#                                 <div style="font-weight: 600; color: #1e293b;">
#                                     {user.username or f'User {user.user}'}
#                                 </div>
#                                 <div style="font-size: 12px; color: #6b7280;">
#                                     ID: {user.user}
#                                 </div>
#                             </div>
#                         </div>
#                         <div style="font-size: 18px; font-weight: 700; color: #3b82f6;">
#                             {user.total_usage or 0}
#                         </div>
#                     </li>
#             '''
#
#         html += '''
#                 </ul>
#             </div>
#         </div>
#
#         <div class="dashboard-grid" style="margin-top: 30px;">
#             <div class="chart-container">
#                 <h3 style="margin: 0 0 25px 0; color: #1e293b; font-size: 20px; font-weight: 700;">
#                     <i class="fas fa-chart-pie" style="margin-right: 10px; color: #8b5cf6;"></i>
#                     Распределение по типам
#                 </h3>
#                 <canvas id="types-chart" height="250"></canvas>
#             </div>
#
#             <div class="chart-container">
#                 <h3 style="margin: 0 0 25px 0; color: #1e293b; font-size: 20px; font-weight: 700;">
#                     <i class="fas fa-clock" style="margin-right: 10px; color: #10b981;"></i>
#                     Статистика периодов
#                 </h3>
#                 <div style="display: grid; gap: 20px;">
#                     <div class="metric-card" style="padding: 25px;">
#                         <div style="display: flex; align-items: center; justify-content: space-between;">
#                             <div>
#                                 <div style="color: #6b7280; font-size: 12px; text-transform: uppercase;">Сегодня</div>
#                                 <div style="font-size: 32px; font-weight: 800; color: #10b981;">{today_answers}</div>
#                             </div>
#                             <i class="fas fa-calendar-day" style="font-size: 32px; color: #e0e7ff;"></i>
#                         </div>
#                     </div>
#                     <div class="metric-card" style="padding: 25px;">
#                         <div style="display: flex; align-items: center; justify-content: space-between;">
#                             <div>
#                                 <div style="color: #6b7280; font-size: 12px; text-transform: uppercase;">За неделю</div>
#                                 <div style="font-size: 32px; font-weight: 800; color: #3b82f6;">{week_answers}</div>
#                             </div>
#                             <i class="fas fa-calendar-week" style="font-size: 32px; color: #e0e7ff;"></i>
#                         </div>
#                     </div>
#                     <div class="metric-card" style="padding: 25px;">
#                         <div style="display: flex; align-items: center; justify-content: space-between;">
#                             <div>
#                                 <div style="color: #6b7280; font-size: 12px; text-transform: uppercase;">За месяц</div>
#                                 <div style="font-size: 32px; font-weight: 800; color: #8b5cf6;">{month_answers}</div>
#                             </div>
#                             <i class="fas fa-calendar-alt" style="font-size: 32px; color: #e0e7ff;"></i>
#                         </div>
#                     </div>
#                 </div>
#             </div>
#
#             <div class="chart-container">
#                 <h3 style="margin: 0 0 25px 0; color: #1e293b; font-size: 20px; font-weight: 700;">
#                     <i class="fas fa-history" style="margin-right: 10px; color: #ef4444;"></i>
#                     Последние скрипты
#                 </h3>
#                 <div style="display: grid; gap: 15px;">
#         '''
#
#         for script in recent_scripts:
#             html += f'''
#                     <div class="metric-card" style="padding: 15px;">
#                         <div style="display: flex; align-items: center; justify-content: space-between;">
#                             <div>
#                                 <div style="font-family: monospace; font-weight: 700; color: #3b82f6;">
#                                     {script.script}
#                                 </div>
#                                 <div style="font-size: 12px; color: #6b7280; margin-top: 5px;">
#                                     {script.owner.username or f'User {script.owner.user}'}
#                                 </div>
#                             </div>
#                             <div class="progress-wrapper" style="width: 100px;">
#                                 <div class="progress-container" style="height: 20px;">
#                                     <div class="progress-bar" data-width="{(script.used / script.max_usage * 100) if script.max_usage > 0 else 0}">
#                                         <span class="progress-text" style="font-size: 10px;">{script.used}/{script.max_usage}</span>
#                                     </div>
#                                 </div>
#                             </div>
#                         </div>
#                     </div>
#             '''
#
#         html += f'''
#                 </div>
#             </div>
#         </div>
#
#         <script>
#             document.addEventListener('DOMContentLoaded', function() {{
#                 const activityCtx = document.getElementById('activity-chart');
#                 if (activityCtx) {{
#                     new Chart(activityCtx.getContext('2d'), {{
#                         type: 'line',
#                         data: {{
#                             labels: {json.dumps([d['date'] for d in usage_by_day])},
#                             datasets: [{{
#                                 label: 'Ответы',
#                                 data: {json.dumps([d['count'] for d in usage_by_day])},
#                                 borderColor: '#3b82f6',
#                                 backgroundColor: 'rgba(59, 130, 246, 0.1)',
#                                 borderWidth: 3,
#                                 tension: 0.4,
#                                 fill: true,
#                                 pointRadius: 6,
#                                 pointHoverRadius: 10,
#                                 pointBackgroundColor: '#3b82f6',
#                                 pointBorderColor: '#fff',
#                                 pointBorderWidth: 2
#                             }}]
#                         }},
#                         options: {{
#                             responsive: true,
#                             maintainAspectRatio: false,
#                             interaction: {{
#                                 intersect: false,
#                                 mode: 'index'
#                             }},
#                             plugins: {{
#                                 legend: {{ display: false }},
#                                 tooltip: {{
#                                     backgroundColor: 'rgba(0, 0, 0, 0.8)',
#                                     padding: 15,
#                                     cornerRadius: 10,
#                                     titleFont: {{ size: 16, weight: 'bold' }},
#                                     bodyFont: {{ size: 14 }}
#                                 }}
#                             }},
#                             scales: {{
#                                 y: {{
#                                     beginAtZero: true,
#                                     grid: {{
#                                         color: 'rgba(0, 0, 0, 0.05)'
#                                     }},
#                                     ticks: {{
#                                         font: {{ size: 12 }}
#                                     }}
#                                 }},
#                                 x: {{
#                                     grid: {{
#                                         display: false
#                                     }},
#                                     ticks: {{
#                                         font: {{ size: 12 }}
#                                     }}
#                                 }}
#                             }}
#                         }}
#                     }});
#                 }}
#
#                 const typesCtx = document.getElementById('types-chart');
#                 if (typesCtx) {{
#                     new Chart(typesCtx.getContext('2d'), {{
#                         type: 'doughnut',
#                         data: {{
#                             labels: {json.dumps([t['script_type'] for t in script_types])},
#                             datasets: [{{
#                                 data: {json.dumps([t['count'] for t in script_types])},
#                                 backgroundColor: [
#                                     '#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444',
#                                     '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
#                                 ],
#                                 borderWidth: 0
#                             }}]
#                         }},
#                         options: {{
#                             responsive: true,
#                             maintainAspectRatio: false,
#                             plugins: {{
#                                 legend: {{
#                                     position: 'bottom',
#                                     labels: {{
#                                         padding: 15,
#                                         font: {{ size: 12 }},
#                                         generateLabels: function(chart) {{
#                                             const data = chart.data;
#                                             return data.labels.map((label, i) => {{
#                                                 const value = data.datasets[0].data[i];
#                                                 const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
#                                                 const percentage = ((value / total) * 100).toFixed(1);
#                                                 return {{
#                                                     text: `${{label}} (${{percentage}}%)`,
#                                                     fillStyle: data.datasets[0].backgroundColor[i],
#                                                     hidden: false,
#                                                     index: i
#                                                 }};
#                                             }});
#                                         }}
#                                     }}
#                                 }},
#                                 tooltip: {{
#                                     backgroundColor: 'rgba(0, 0, 0, 0.8)',
#                                     padding: 12,
#                                     cornerRadius: 8
#                                 }}
#                             }}
#                         }}
#                     }});
#                 }}
#             }});
#         </script>
#         '''
#
#         return html
#
#
# JAZZMIN_SETTINGS = {
#     "site_title": "Script Admin",
#     "site_header": "Script Management",
#     "site_brand": "SMS",
#     "site_logo": None,
#     "welcome_sign": "Добро пожаловать в панель управления",
#     "copyright": "Script Management System © 2024",
#
#     "topmenu_links": [
#         {"name": "Главная", "url": "admin:index", "permissions": ["auth.view_user"]},
#         {"name": "Пользователи", "url": "admin:v1_tgusers_changelist"},
#         {"name": "Скрипты", "url": "admin:v1_idscript_changelist"},
#         {"name": "Ответы", "url": "admin:v1_answer_changelist"},
#         {"name": "Рефералы", "url": "admin:v1_referral_changelist"},
#     ],
#
#     "show_sidebar": True,
#     "navigation_expanded": True,
#     "hide_apps": [],
#     "hide_models": [],
#
#     "icons": {
#         "auth": "fas fa-users-cog",
#         "auth.user": "fas fa-user",
#         "auth.Group": "fas fa-users",
#         "v1.TgUsers": "fas fa-user-circle",
#         "v1.IdScript": "fas fa-code",
#         "v1.Answer": "fas fa-comment-dots",
#         "v1.Referral": "fas fa-share-alt",
#     },
#
#     "default_icon_parents": "fas fa-chevron-circle-right",
#     "default_icon_children": "fas fa-circle",
#
#     "use_google_fonts_cdn": True,
#     "show_ui_builder": False,
#
#     "changeform_format": "horizontal_tabs",
#     "changeform_format_overrides": {
#         "v1.tgusers": "collapsible",
#         "v1.idscript": "vertical_tabs",
#     },
# }
#
#
# def owner_display(self, obj):
#     avatar_letter = (obj.owner.username[0] if obj.owner.username else "U").upper()
#     return format_html(
#         '<a href="{}" style="display: flex; align-items: center; gap: 10px;">'
#         '<span class="user-avatar" style="width: 30px; height: 30px; font-size: 14px; '
#         'background: #e0e7ff; border-radius: 50%; display: flex; justify-content: center; '
#         'align-items: center;">{}</span>'
#         '<span style="font-weight: 600; color: #4c1d95;">{}</span>'
#         '</a>',
#         obj.owner.get_absolute_url() if hasattr(obj.owner, 'get_absolute_url') else "#",
#         avatar_letter,
#         obj.owner.username or f'User {obj.owner.id}'
#     )
#
# owner_display.short_description = 'Владелец'
#
#
# def type_display(self, obj):
#     colors = {
#         'base_prof_uuid': 'linear-gradient(135deg, #3b82f6, #2563eb)',
#     }
#     color = colors.get(obj.script_type, 'linear-gradient(135deg, #6b7280, #4b5563)')
#     return format_html(
#         '<span style="padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; '
#         'background: {}; color: white;">{}</span>',
#         color, obj.get_script_type_display()
#     )
#
# type_display.short_description = 'Тип'
#
#
# def type_display(self, obj):
#     colors = {
#         'base_prof_uuid': 'linear-gradient(135deg, #3b82f6, #2563eb)',
#     }
#     color = colors.get(obj.script_type, 'linear-gradient(135deg, #6b7280, #4b5563)')
#     return format_html(
#         '<span style="padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; '
#         'background: {}; color: white;">{}</span>',
#         color, obj.get_script_type_display()
#     )
#
#
# type_display.short_description = 'Тип'
#
#
# def status_display(self, obj):
#     if not obj or not obj.pk:
#         return format_html('<span class="status-badge status-inactive">Новый</span>')
#
#     now = timezone.now()
#     if not obj.is_active:
#         return format_html('<span class="status-badge status-inactive">Выключен</span>')
#     elif obj.is_max_usage_reached:
#         return format_html('<span class="status-badge status-expired">Лимит исчерпан</span>')
#     elif obj.start_at and obj.start_at > now:
#         return format_html('<span class="status-badge status-pending">Ожидает запуска</span>')
#     elif obj.stop_at and obj.stop_at < now:
#         return format_html('<span class="status-badge status-expired">Время истекло</span>')
#     else:
#         return format_html('<span class="status-badge status-active">Активен</span>')
#
#
# status_display.short_description = 'Статус'
#
#
# def usage_progress(self, obj):
#     percentage = (obj.used / obj.max_usage * 100) if obj.max_usage > 0 else 0
#     color = '#22c55e' if percentage < 50 else '#f59e0b' if percentage < 80 else '#ef4444'
#
#     return format_html(
#         '''<div class="progress-wrapper">
#             <div class="progress-container">
#                 <div class="progress-bar" data-width="{}" style="background: linear-gradient(90deg, {}, {});">
#                     <span class="progress-text">{}/{}</span>
#                 </div>
#             </div>
#         </div>''',
#         percentage, color, color, obj.used, obj.max_usage
#     )
#
#
# usage_progress.short_description = 'Использование'
#
#
# def fingerprint_display(self, obj):
#     if obj.fingerprint:
#         return format_html(
#             '<div style="display: flex; align-items: center; gap: 8px;">'
#             '<span class="fingerprint-icon"></span>'
#             '<span style="font-family: monospace; font-size: 12px; color: #10b981;" title="{}">'
#             '{}...</span>'
#             '</div>',
#             obj.fingerprint, obj.fingerprint[:16]
#         )
#     return format_html('<span style="color: #9ca3af;">Не привязан</span>')
#
#
# fingerprint_display.short_description = 'Fingerprint'
#
#
# def time_remaining(self, obj):
#     if not obj or not obj.pk or not obj.stop_at:
#         return format_html('<span style="color: #9ca3af;">—</span>')
#
#     now = timezone.now()
#     if obj.stop_at < now:
#         return format_html(
#             '<span class="time-badge" style="background: linear-gradient(135deg, #ef4444, #dc2626);">Истёк</span>')
#
#     delta = obj.stop_at - now
#     days = delta.days
#     hours = delta.seconds // 3600
#
#     if days > 7:
#         return format_html(
#             '<span class="time-badge" style="background: linear-gradient(135deg, #10b981, #059669);">{} дней</span>',
#             days)
#     elif days > 0:
#         return format_html(
#             '<span class="time-badge" style="background: linear-gradient(135deg, #3b82f6, #2563eb);">{} дн. {} ч.</span>',
#             days, hours)
#     elif hours > 0:
#         return format_html(
#             '<span class="time-badge" style="background: linear-gradient(135deg, #f59e0b, #d97706);">{} часов</span>',
#             hours)
#     else:
#         minutes = delta.seconds // 60
#         return format_html(
#             '<span class="time-badge" style="background: linear-gradient(135deg, #ef4444, #dc2626);">{} мин.</span>',
#             minutes)
#
#
# time_remaining.short_description = 'Осталось'
#
#
# def actions_display(self, obj):
#     answers_count = getattr(obj, '_answers_count', 0)
#     answers_url = reverse('admin:v1_answer_changelist') + f'?script__id__exact={obj.id}'
#
#     return format_html(
#         '<div style="display: flex; gap: 8px;">'
#         '<a href="{}" class="action-button">'
#         '<i class="fas fa-comments"></i> Ответы ({})'
#         '</a>'
#         '</div>',
#         answers_url, answers_count
#     )
#
#
# actions_display.short_description = 'Действия'
#
#
# def analytics_dashboard(self, obj):
#     if not obj or not obj.id:
#         return format_html('<span style="color: #9ca3af;">Аналитика будет доступна после сохранения</span>')
#
#     answers_count = obj.answers.count()
#     last_answer = obj.answers.order_by('-created_at').first()
#     last_used = getattr(obj, '_last_used', None)
#     days_active = (timezone.now() - obj.created_at).days
#     avg_per_day = obj.used / max(days_active, 1)
#
#     html = f'''
#         <div class="dashboard-grid">
#             <div class="chart-container" style="grid-column: span 2;">
#                 <h3 style="margin: 0 0 20px 0; color: #4c1d95;">
#                     <i class="fas fa-chart-area" style="margin-right: 10px;"></i>
#                     График использования
#                 </h3>
#                 <canvas id="usage-chart-{obj.id}" height="300"></canvas>
#             </div>
#
#             <div class="stat-card">
#                 <h3 style="margin: 0 0 20px 0; color: #4c1d95;">
#                     <i class="fas fa-info-circle" style="margin-right: 10px;"></i>
#                     Ключевые метрики
#                 </h3>
#                 <div style="display: grid; gap: 15px;">
#                     <div class="metric-card">
#                         <div style="color: #6b7280; font-size: 12px;">Всего ответов</div>
#                         <div style="font-size: 24px; font-weight: 700; color: #3b82f6;">{answers_count}</div>
#                     </div>
#                     <div class="metric-card">
#                         <div style="color: #6b7280; font-size: 12px;">Среднее в день</div>
#                         <div style="font-size: 24px; font-weight: 700; color: #10b981;">{avg_per_day:.1f}</div>
#                     </div>
#                     <div class="metric-card">
#                         <div style="color: #6b7280; font-size: 12px;">Последнее использование</div>
#                         <div style="font-size: 14px; font-weight: 600; color: #6366f1;">
#                             {last_used.strftime('%d.%m.%Y %H:%M') if last_used else 'Никогда'}
#                         </div>
#                     </div>
#                 </div>
#             </div>
#         </div>
#
#         <script>
#             (function() {{
#                 const ctx = document.getElementById('usage-chart-{obj.id}');
#                 if (ctx) {{
#                     const labels = [];
#                     const data = [];
#
#                     for (let i = 6; i >= 0; i--) {{
#                         const date = new Date();
#                         date.setDate(date.getDate() - i);
#                         labels.push(date.toLocaleDateString('ru-RU', {{ day: 'numeric', month: 'short' }}));
#                         data.push(Math.floor(Math.random() * 20) + 5);
#                     }}
#
#                     new Chart(ctx.getContext('2d'), {{
#                         type: 'line',
#                         data: {{
#                             labels: labels,
#                             datasets: [{{
#                                 label: 'Использований',
#                                 data: data,
#                                 borderColor: '#8b5cf6',
#                                 backgroundColor: 'rgba(139, 92, 246, 0.1)',
#                                 borderWidth: 3,
#                                 tension: 0.4,
#                                 fill: true,
#                                 pointRadius: 5,
#                                 pointHoverRadius: 8,
#                                 pointBackgroundColor: '#8b5cf6',
#                                 pointBorderColor: '#fff',
#                                 pointBorderWidth: 2
#                             }}]
#                         }},
#                         options: {{
#                             responsive: true,
#                             maintainAspectRatio: false,
#                             interaction: {{
#                                 intersect: false,
#                                 mode: 'index'
#                             }},
#                             plugins: {{
#                                 legend: {{ display: false }},
#                                 tooltip: {{
#                                     backgroundColor: 'rgba(0, 0, 0, 0.8)',
#                                     padding: 12,
#                                     cornerRadius: 8,
#                                     titleFont: {{ size: 14 }},
#                                     bodyFont: {{ size: 13 }}
#                                 }}
#                             }},
#                             scales: {{
#                                 y: {{
#                                     beginAtZero: true,
#                                     grid: {{
#                                         color: 'rgba(0, 0, 0, 0.05)'
#                                     }}
#                                 }},
#                                 x: {{
#                                     grid: {{
#                                         display: false
#                                     }}
#                                 }}
#                             }}
#                         }}
#                     }});
#                 }}
#             }})();
#         </script>
#         '''
#
#     return mark_safe(html)
#
#
# analytics_dashboard.short_description = 'Аналитика'
#
#
# @admin.register(Answer)
# class AnswerAdmin(CustomAdminMixin, admin.ModelAdmin):
#     list_display = ('id', 'script_display', 'owner_display', 'image_display',
#                     'answer_display', 'created_display')
#     list_filter = ('created_at', 'script__script_type')
#     search_fields = ('script__script', 'script__owner__username')
#     readonly_fields = ('created_at', 'updated_at', 'detailed_view')
#     list_per_page = 30
#
#     fieldsets = (
#         ('📝 Основная информация', {
#             'fields': ('script',),
#             'classes': ('wide',)
#         }),
#         ('🖼️ Изображение', {
#             'fields': ('image', 'detailed_view'),
#             'classes': ('wide',)
#         }),
#         ('💬 Ответ', {
#             'fields': ('answer',),
#             'classes': ('wide',)
#         }),
#         ('🕐 Временные метки', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
#
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related('script', 'script__owner')
#
#     def script_display(self, obj):
#         url = reverse('admin:v1_idscript_change', args=[obj.script.id])
#         return format_html(
#             '<a href="{}" style="text-decoration: none; font-family: monospace; '
#             'font-size: 14px; font-weight: 700; color: #3b82f6;">{}</a>',
#             url, obj.script.script
#         )
#
#     script_display.short_description = 'Скрипт'
#
#     def owner_display(self, obj):
#         owner = obj.script.owner
#         url = reverse('admin:v1_tgusers_change', args=[owner.id])
#         avatar_letter = owner.username[0].upper() if owner.username else str(owner.user)[0]
#
#         return format_html(
#             '<a href="{}" style="text-decoration: none; display: flex; align-items: center; gap: 8px;">'
#             '<span class="user-avatar" style="width: 25px; height: 25px; font-size: 12px;">{}</span>'
#             '<span style="font-weight: 500; color: #4c1d95;">{}</span>'
#             '</a>',
#             url, avatar_letter, owner.username or f'User {owner.user}'
#         )
#
#     owner_display.short_description = 'Владелец'
#
#     def image_display(self, obj):
#         if obj.image:
#             return format_html(
#                 '<img src="{}" class="image-preview" alt="Answer image" />',
#                 obj.image.url
#             )
#         return format_html('<span style="color: #9ca3af;">Нет изображения</span>')
#
#     image_display.short_description = 'Изображение'
#
#     def answer_display(self, obj):
#         if obj.answer:
#             answer_str = json.dumps(obj.answer, ensure_ascii=False, indent=2)
#             if len(answer_str) > 100:
#                 preview = answer_str[:100] + '...'
#             else:
#                 preview = answer_str
#
#             return format_html(
#                 '<div class="answer-preview">{}</div>',
#                 preview
#             )
#         return format_html('<span style="color: #9ca3af;">Нет ответа</span>')
#
#     answer_display.short_description = 'Ответ'
#
#     def created_display(self, obj):
#         time_ago = timezone.now() - obj.created_at
#
#         if time_ago.days == 0:
#             if time_ago.seconds < 3600:
#                 text = f'{time_ago.seconds // 60} мин. назад'
#                 color = '#10b981'
#             else:
#                 text = f'{time_ago.seconds // 3600} ч. назад'
#                 color = '#3b82f6'
#         elif time_ago.days == 1:
#             text = 'Вчера'
#             color = '#6366f1'
#         elif time_ago.days < 7:
#             text = f'{time_ago.days} дн. назад'
#             color = '#8b5cf6'
#         else:
#             text = obj.created_at.strftime('%d.%m.%Y %H:%M')
#             color = '#6b7280'
#
#         return format_html(
#             '<span style="color: {}; font-weight: 500;">{}</span>',
#             color, text
#         )
#
#     created_display.short_description = 'Создано'
#     created_display.admin_order_field = 'created_at'
#
#     def detailed_view(self, obj):
#         if obj.id and obj.image:
#             return format_html(
#                 '<div style="background: #f8f9ff; padding: 20px; border-radius: 15px; margin: 20px 0;">'
#                 '<img src="{}" style="max-width: 100%; height: auto; border-radius: 10px; '
#                 'box-shadow: 0 10px 30px rgba(0,0,0,0.1);" />'
#                 '</div>',
#                 obj.image.url
#             )
#         return '—'
#
#     detailed_view.short_description = 'Полный просмотр'
