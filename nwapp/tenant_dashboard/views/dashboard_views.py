from rest_framework import status, response, views

from shared_foundation.drf.permissions import DisableOptionsPermission, TenantPermission
from tenant_dashboard.serializers import DashboardSerializer


class DashboardAPI(views.APIView):
    throttle_classes = ()
    permission_classes = (
        DisableOptionsPermission,
        TenantPermission,
    )

    def get(self, request):
        serializer = DashboardSerializer(request)
        return response.Response(
            status=status.HTTP_200_OK,
            data=serializer.data
        )
