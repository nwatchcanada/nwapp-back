from rest_framework import status, response, views, permissions

from shared_foundation.drf.permissions import SharedUserIsActivePermission, DisableOptionsPermission, TenantPermission
from tenant_dashboard.serializers import StaffDashboardSerializer


class DashboardAPI(views.APIView):
    throttle_classes = ()
    permission_classes = (
        DisableOptionsPermission,
        permissions.IsAuthenticated,
        SharedUserIsActivePermission,
        TenantPermission,
    )

    def get(self, request):
        serializer = None
        if request.user.is_executive or request.user.is_management or request.user.is_frontline:
            serializer = StaffDashboardSerializer(request)
        else:
            #TODO: IMPLEMENT DASHBOARD API BASED ON USER ROLE.
            return Response(
                data={
                    'error': "Programmer needs to support this user type."
                },
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
        return response.Response(
            status=status.HTTP_200_OK,
            data=serializer.data
        )
