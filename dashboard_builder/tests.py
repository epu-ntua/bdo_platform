from django.test import TestCase
from models import Dashboard
import json
from django.test import Client


class TestDashboardCreation(TestCase) :

    def test_only_one_visualization(self):
        dashboardTitle = "A title"
        dashboardPrivate = True
        tempVis1 = ["tempviz.com", "1", "1", "1", "1", "temptitle", ""]
        payload = {"title": dashboardTitle, "private": dashboardPrivate, "0": tempVis1}
        payload = json.dumps(payload)
        payloadContainer = {payload: ''}

        cl = Client()
        url = "http://localhost:8000/dashboards/save/"

        pk = cl.post(url, data=payloadContainer)
        print pk
        pk = pk.content
        pk = json.loads(pk)
        pk = pk["pk"]
        dashboard = Dashboard.objects.get(pk=pk)

        self.assertEqual(str(dashboard.title) , str(dashboardTitle))
        self.assertEqual(dashboard.private , dashboardPrivate)
        tempCounter = 0
        for x in tempVis1:
            self.assertEqual(str(dashboard.viz_components["0"][tempCounter]), str(x))
            tempCounter += 1