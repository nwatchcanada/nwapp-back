from django.urls import path

from tenant_report.views.csv.report_01_view import report_01_streaming_csv_view
from tenant_report.views.csv.report_02_view import report_02_streaming_csv_view
from tenant_report.views.csv.report_03_view import report_03_streaming_csv_view
from tenant_report.views.csv.report_04_view import report_04_streaming_csv_view


urlpatterns = (
    path('api/v1/report/1/csv-download', report_01_streaming_csv_view, name='nwapp_tenant_report_01_download_csv_file_api_endpoint'),
    path('api/v1/report/2/csv-download', report_02_streaming_csv_view, name='nwapp_tenant_report_02_download_csv_file_api_endpoint'),
    path('api/v1/report/3/csv-download', report_03_streaming_csv_view, name='nwapp_tenant_report_03_download_csv_file_api_endpoint'),
    path('api/v1/report/4/csv-download', report_04_streaming_csv_view, name='nwapp_tenant_report_04_download_csv_file_api_endpoint'),
)
