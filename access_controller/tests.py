from django.test import TestCase
from dashboard_builder.models import Dashboard, DashboardAccessRequest
import json
from django.test import Client
from django.contrib.auth.models import User
from access_controller.policy_enforcement_point import PEP



class TestDashboardCreation(TestCase) :

    def test_access_to_dashboard(self):
        dashboardTitle = "A title 2"
        dashboardPrivate = True
        tempVis2 = ["", "1", "1", "1", "1", "temptitle", "<div>Hello this is a test</div>"]
        payload = {"title": dashboardTitle, "private": dashboardPrivate, "0": tempVis2, "can_be_shared": True}
        payload = json.dumps(payload)
        payloadContainer = {payload: ''}
        another_user = User(username='another_user_a')
        another_user.save()
        user = User(username='testuser_a')
        user.save()
        cl = Client()
        cl.force_login(user)
        url = "http://localhost:8000/dashboards/save/"
        pk = cl.post(url, data=payloadContainer)
        pk = pk.content
        pk = json.loads(pk)
        accessible_dashboard_pk = pk["pk"]

        den_dashboard = Dashboard(user=another_user, viz_components={}, private=True, can_be_shared=True)
        den_dashboard.save()
        non_accessible_dashboard_pk = den_dashboard.id

        from django.http import HttpRequest
        request1 = HttpRequest()
        request1.user = user
        decision = PEP.access_to_dashboard(request1, accessible_dashboard_pk)
        self.assertEqual(str(decision), str(True))

        decision = PEP.access_to_dashboard(request1, non_accessible_dashboard_pk)
        self.assertEqual(str(decision), str(False))

        decision = PEP.access_to_edit_dashboard(request1, accessible_dashboard_pk)
        self.assertEqual(str(decision), str(True))

        decision = PEP.access_to_edit_dashboard(request1, non_accessible_dashboard_pk)
        self.assertEqual(str(decision), str(False))
        # Log out user. Log in the other user. Create request. Accept request to view dashboard (not to edit). Check
        # again.
        cl.logout()
        cl = Client()
        cl.force_login(another_user)
        resource = den_dashboard
        new_access_request = DashboardAccessRequest(user=user, resource=resource)
        new_access_request.save()
        request_id = new_access_request.id
        url = "http://localhost:8000/access_control/share_access_to_resource/dashboard/"
        payload = {"request_id": request_id}
        cl.post(url, data=payload)

        decision = PEP.access_to_dashboard(request1, non_accessible_dashboard_pk)
        self.assertEqual(str(decision), str(True))

    def test_generating_access_to_dashboard(self):
        dashboardTitle = "A title"
        dashboardPrivate = True
        tempVis2 = ["", "1", "1", "1", "1", "temptitle", "<div>Hello this is a test</div>"]
        payload = {"title": dashboardTitle, "private": dashboardPrivate, "0": tempVis2, "can_be_shared": True}
        payload = json.dumps(payload)
        payloadContainer = {payload: ''}

        user = User(username='testuser_a1')
        user.save()
        cl = Client()
        cl.force_login(user)
        url = "http://localhost:8000/dashboards/save/"
        pk = cl.post(url, data=payloadContainer)
        pk = pk.content
        pk = json.loads(pk)
        accessible_dashboard_pk = pk["pk"]

        from django.http import HttpRequest
        request1 = HttpRequest()
        request1.user = user
        decision = PEP.access_to_dashboard(request1, accessible_dashboard_pk)
        self.assertEqual(str(decision), str(True))

        another_user = User(username='another_testuser_a1')
        another_user.save()
        cl.logout()
        cl = Client()
        cl.force_login(another_user)

        url = "http://localhost:8000/access_control/request_access_to_resource/dashboard/"
        payload = {"resource_id": accessible_dashboard_pk}
        response = cl.post(url, data=payload)
        self.assertEqual(response.status_code, 200)

    def test_responding_to_access_request_to_dashboard(self):
        dashboardTitle = "A title"
        dashboardPrivate = True
        tempVis2 = ["", "1", "1", "1", "1", "temptitle", "<div>Hello this is a test</div>"]
        payload = {"title": dashboardTitle, "private": dashboardPrivate, "0": tempVis2, "can_be_shared": True}
        payload = json.dumps(payload)
        payloadContainer = {payload: ''}
        another_user = User(username='another_user_a2')
        another_user.save()
        user = User(username='testuser_a2')
        user.save()
        cl = Client()
        cl.force_login(user)
        url = "http://localhost:8000/dashboards/save/"
        pk = cl.post(url, data=payloadContainer)
        pk = pk.content
        pk = json.loads(pk)
        accessible_dashboard_pk = pk["pk"]


        # Log out user. Log in the other user. Create request. Accept request to view dashboard (not to edit). Check
        # again.
        cl.logout()
        cl = Client()
        cl.force_login(another_user)
        resource = Dashboard.objects.get(id=accessible_dashboard_pk)
        new_access_request = DashboardAccessRequest(user=another_user, resource=resource)
        new_access_request.save()
        request_id = new_access_request.id

        cl.logout()
        cl = Client()
        cl.force_login(user)

        url = "http://localhost:8000/access_control/share_access_to_resource/dashboard/"
        payload = {"request_id": request_id}
        cl.post(url, data=payload)

        accepted_access_request_obj = DashboardAccessRequest.objects.get(id=request_id)

        self.assertEqual(accepted_access_request_obj.status, 'accepted')
        accepted_access_request_obj.delete()

        cl.logout()
        cl = Client()
        cl.force_login(another_user)
        resource = Dashboard.objects.get(id=accessible_dashboard_pk)
        new_access_request2 = DashboardAccessRequest(user=another_user, resource=resource)
        new_access_request2.save()
        request_id2 = new_access_request2.id

        cl.logout()
        cl = Client()
        cl.force_login(user)

        url = "http://localhost:8000/access_control/reject_access_to_resource/dashboard/"
        payload = {"request_id": request_id2}
        cl.post(url, data=payload)
        rejected_access_request_obj = DashboardAccessRequest.objects.get(id=request_id2)
        self.assertEqual(rejected_access_request_obj.status, 'rejected')

