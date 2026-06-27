from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('',                    views.reports_index,         name='index'),
    path('members/excel/',      views.export_members_excel,  name='members_excel'),
    path('members/csv/',        views.export_members_csv,    name='members_csv'),
    path('members/pdf/',        views.export_members_pdf,    name='members_pdf'),
    path('help/excel/',         views.export_help_excel,     name='help_excel'),
    path('pmf/excel/',          views.export_pmf_excel,      name='pmf_excel'),
]
