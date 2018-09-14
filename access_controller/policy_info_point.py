from models import *
from dashboard_builder.models import Dashboard, DashboardAccess


class PIP:

    def __init__(self):
        pass

    @staticmethod
    def getDashboardPolicies():
        return [PublicResourcePolicy(), OwnerPolicy(), AccessGrantedPolicy()]

    @staticmethod
    def getDashboardInfo(dashboard_id):
        response = dict()
        dashboard = Dashboard.objects.get(pk=dashboard_id)
        response['dashboard_owner'] = dashboard.user
        response['dashboard_private'] = dashboard.private
        response['access_list'] = [{"user": acc.user, "start": acc.start, "end": acc.end, "valid": acc.valid, }
                                   for acc in DashboardAccess.objects.filter(dashboard=dashboard)]
        return response
