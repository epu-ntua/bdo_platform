from models import *
from dashboard_builder.models import Dashboard, DashboardAccess
from service_builder.models import Service, ServiceAccess

class PIP:

    def __init__(self):
        pass

    @staticmethod
    def getDashboardPolicies():
        return [PublicResourcePolicy(), OwnerPolicy(), AccessGrantedPolicy()]

    @staticmethod
    def getServicePolicies():
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

    @staticmethod
    def getServiceInfo(service_id):
        response = dict()
        service = Service.objects.get(pk=service_id)
        response['service_owner'] = service.user
        response['service_private'] = service.private
        response['access_list'] = [{"user": acc.user, "start": acc.start, "end": acc.end, "valid": acc.valid, }
                                   for acc in ServiceAccess.objects.filter(service=service)]
        return response
