from policy_info_point import PIP

class PDP:

    def __init__(self):
        pass

    @staticmethod
    def resolve_access_to_dataset(user, time, dataset_id):
        print(
            """   Resolving access for: 
            Dataset: {0}
            User: {1}
            Time: {2}
            """.format(dataset_id, user, time))
        request_time = time
        request_user = user

        policies = PIP.getDatasetPolicies()

        dataset_info = PIP.getDatasetInfo(dataset_id)
        print ("""Dataset Info: """)
        print dataset_info
        input = {
            "request_user": request_user,
            "request_time": request_time,
            "resource_owner": dataset_info["dataset_owner"],
            "resource_private": dataset_info["dataset_private"],
            "access_list": dataset_info["access_list"],
        }

        for pol in policies:
            if pol.evaluate(input) is True:
                return True

        return False



    @staticmethod
    def resolve_access_to_dashboard(user, time, dashboard_id):
        print(
        """   Resolving access for: 
        Dashboard: {0}
        User: {1}
        Time: {2}
        """.format(dashboard_id, user, time))
        request_time = time
        request_user = user

        policies = PIP.getDashboardPolicies()
        dashboard_info = PIP.getDashboardInfo(dashboard_id)
        print ("""Dashboard Info: """)
        print dashboard_info
        input = {
            "request_user": request_user,
            "request_time": request_time,
            "resource_owner": dashboard_info["dashboard_owner"],
            "resource_private": dashboard_info["dashboard_private"],
            "access_list": dashboard_info["access_list"],
        }

        for pol in policies:
            if pol.evaluate(input) is True:
                return True

        return False

    @staticmethod
    def resolve_access_to_service(user, time, service_id):
        print(
            """   Resolving access for: 
            Service: {0}
            User: {1}
            Time: {2}
            """.format(service_id, user, time))
        request_time = time
        request_user = user

        policies = PIP.getServicePolicies()
        service_info = PIP.getServiceInfo(service_id)
        print ("""Service Info: """)
        print service_info
        input = {
            "request_user": request_user,
            "request_time": request_time,
            "resource_owner": service_info["service_owner"],
            "resource_private": service_info["service_private"],
            "access_list": service_info["access_list"],
        }

        for pol in policies:
            if pol.evaluate(input) is True:
                return True

        return False
