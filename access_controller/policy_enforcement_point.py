from datetime import datetime
from policy_decision_point import *


class PEP:

    def __init__(self):
        pass

    @staticmethod
    def access_to_dataset_for_query(request, dataset_id):
        request_user = request.user
        request_time = datetime.now()
        decision = PDP.resolve_access_to_dataset(request_user, request_time, dataset_id)
        return decision

    @staticmethod
    def access_to_dataset_for_preview(self):
        pass

    @staticmethod
    def access_to_dashboard(request, dashboard_id):
        request_user = request.user
        request_time = datetime.now()
        decision = PDP.resolve_access_to_dashboard(request_user, request_time, dashboard_id)
        return decision

    @staticmethod
    def access_to_service(request, service_id):
        request_user = request.user
        request_time = datetime.now()
        decision = PDP.resolve_access_to_service(request_user, request_time, service_id)
        return decision
