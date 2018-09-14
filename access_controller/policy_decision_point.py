from policy_info_point import PIP

class PDP:

    def __init__(self):
        pass

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
