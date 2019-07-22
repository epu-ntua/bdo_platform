from django.test import TestCase
from models import Dashboard
import json
from django.test import Client
from django.contrib.auth.models import User


class TestDashboardCreation(TestCase) :

    def test_only_one_visualization(self):
        dashboardTitle = "A title"
        dashboardPrivate = True
        tempVis1 = ["tempviz.com", "1", "1", "1", "1", "temptitle", ""]
        payload = {"title": dashboardTitle, "private": dashboardPrivate, "0": tempVis1, "can_be_shared": True}
        payload = json.dumps(payload)
        payloadContainer = {payload: ''}


        user = User(username='testuser')
        user.save()
        cl = Client()
        cl.force_login(user)
        url = "http://localhost:8000/dashboards/save/"

        pk = cl.post(url, data=payloadContainer)
        print pk
        pk = pk.content
        pk = json.loads(pk)
        pk = pk["pk"]
        try:
            dashboard = Dashboard.objects.get(pk=pk)
        except:
            dashboard = None

        self.assertEqual(str(dashboard.title) , str(dashboardTitle))
        self.assertEqual(dashboard.private , dashboardPrivate)
        tempCounter = 0
        for x in tempVis1:
            self.assertEqual(str(dashboard.viz_components["0"][tempCounter]), str(x))
            tempCounter += 1




    def test_update_function_visualization(self):
        dashboardTitle = "A title"
        dashboardPrivate = True
        tempVis1 = ["tempviz.com", "1", "1", "1", "1", "temptitle", ""]
        payload = {"title": dashboardTitle, "private": dashboardPrivate, "0": tempVis1, "can_be_shared": True}
        payload = json.dumps(payload)
        payloadContainer = {payload: ''}

        user = User(username='testuser')
        user.save()
        cl = Client()
        cl.force_login(user)
        url = "http://localhost:8000/dashboards/save/"

        pk = cl.post(url, data=payloadContainer)
        pk = pk.content
        pk = json.loads(pk)
        pk = pk["pk"]

        dashboardPrivate = False
        dashboardTitle = "Updated title"
        tempVis1 = ["tempviz2.com", "2", "2", "2", "2", "temptitle2", ""]
        payload = {"title": dashboardTitle, "private": dashboardPrivate, "0": tempVis1, "can_be_shared": True}
        payload = json.dumps(payload)
        payloadContainer = {payload: ''}

        url = "http://localhost:8000/dashboards/save/" + str(pk) + "/"

        pk2 = cl.post(url, data=payloadContainer)
        pk2 = pk2.content
        pk2 = json.loads(pk2)
        pk2 = pk2["pk"]

        try:
            dashboard = Dashboard.objects.get(pk=pk2)
        except:
            dashboard = None

        self.assertEqual(pk, pk2)
        self.assertEqual(str(dashboard.title), str(dashboardTitle))
        self.assertEqual(dashboard.private , dashboardPrivate)
        tempCounter = 0
        for x in tempVis1:
            self.assertEqual(dashboard.viz_components["0"][tempCounter], x)
            tempCounter += 1




    def test_multiple_visualization(self):
        dashboardTitle = "A title 2"
        dashboardPrivate = True
        tempVis1 = ["tempviz.com", "1", "1", "1", "1", "temptitle", ""]
        tempVis2 = ["", "1", "1", "1", "1", "temptitle", "<div>Hello this is a test</div>"]
        payload = {"title": dashboardTitle, "private": dashboardPrivate, "0": tempVis1, "1": tempVis2, "can_be_shared": True}
        payload = json.dumps(payload)
        payloadContainer = {payload: ''}

        user = User(username='testuser_d')
        user.save()
        cl = Client()
        cl.force_login(user)
        url = "http://localhost:8000/dashboards/save/"

        pk = cl.post(url, data=payloadContainer)
        pk = pk.content
        pk = json.loads(pk)
        pk = pk["pk"]
        dashboard = Dashboard.objects.get(pk=pk)

        self.assertEqual(str(dashboard.title), str(dashboardTitle))
        self.assertEqual(dashboard.private, dashboardPrivate)
        tempCounter = 0
        for x in tempVis1:
            self.assertEqual(dashboard.viz_components["0"][tempCounter], x)
            tempCounter += 1

        tempCounter = 0
        for x in tempVis2:
            self.assertEqual(dashboard.viz_components["1"][tempCounter], x)
            tempCounter += 1
