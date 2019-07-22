from django.test import TestCase
from dashboard_builder.models import Dashboard, DashboardAccessRequest
import json
from django.test import Client
from django.contrib.auth.models import User
from access_controller.policy_enforcement_point import PEP
from query_designer.models import *
import textwrap
from datetime import datetime
from service_builder.models import Service




class TestDashboardCreation(TestCase):

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


class TestAccessControllerPermissionIntegration(TestCase):
    # def test_access_to_execute_service(self):
    #     user = User(username='testuser_s_zero')
    #     user.save()
    #     cl = Client()
    #     cl.force_login(user)
    #     selected_queries_dict = {"Q1": {"query_id": "313", "paragraphs": ["20180501-135246_1102090558"]}}
    #     selected_queries = json.dumps(selected_queries_dict)
    #     # print selected_queries
    #     arguments_dict = {"filter-arguments": [],
    #         "algorithm-arguments": []}
    #     arguments = json.dumps(arguments_dict)
    #     # print arguments
    #     notebook_id = "2DP3SVY7D"
    #     # print notebook_id
    #     output_html = textwrap.dedent(
    #         """<div id="service_container" class="text-center">
    #                 <div id="service_config_container" class="text-center">
    #                     <button type="button" id="argsCollapseBtn" class="btn btn-md btn-primary" data-toggle="collapse" data-target="#serviceConfigCollapse">
    #                       Configure
    #                     </button>
    #                     <div id="serviceConfigCollapse" class="collapse in" >
    #                         <div class="well">
    #                             <h4 class="modal-title">Please give your input</h4>
    #                             <form id="service_args_container" class="modal-body" style="padding: 0 25%">
    #
    #                             </form>
    #                             <button type="button" class="btn btn-success" data-toggle="collapse" data-target="#serviceConfigCollapse" id="submitServiceConfig">Submit</button>
    #                             <button type="button" class="btn btn-default" data-toggle="collapse" data-target="#serviceConfigCollapse">Cancel</button>
    #                         </div>
    #                     </div>
    #                 </div>
    #
    #                 <div id="service_result_container" class="text-center">
    #                     {% load static %}
    #                     <div class="loadingDiv">
    #                         <img src="http://assets.motherjones.com/interactives/projects/features/koch-network/shell19/img/loading.gif"/>
    #                     </div>
    #
    #                     <table class="table table-full-width">
    #                         <thead>
    #                             <tr>
    #                                 <th>Maximum Height</th><th>Average Height</th><th>Standard Deviation</th>
    #                             </tr>
    #                         </thead>
    #                         <tbody>
    #                             <tr>
    #                                 <td>{{ result.max_height }}</td><td>{{ result.av_height }}</td><td>{{ result.stand_dev_height }}</td>
    #                             </tr>
    #                         </tbody>
    #                     </table>
    #
    #                     <table class="table table-full-width">
    #                         <thead>
    #                             <tr>
    #                                 <th>Maximum Period</th><th>Average Period</th><th>Standard Deviation</th>
    #                             </tr>
    #                         </thead>
    #                         <tbody>
    #                             <tr>
    #                                 <td>{{ result.max_period }}</td><td>{{ result.av_period }}</td><td>{{ result.stand_dev_period }}</td>
    #                             </tr>
    #                         </tbody>
    #                     </table>
    #
    #                     <div class="panel-group row">
    #                         <div class="panel panel-default col-sm-3">
    #                             <div class="panel-heading">Maximum Power</div>
    #                             <div class="panel-body">{{ result.max_power }}</div>
    #                         </div>
    #                         <div class="panel panel-default col-sm-3">
    #                             <div class="panel-heading">Minimum Power</div>
    #                             <div class="panel-body">{{ result.min_power }}</div>
    #                         </div>
    #                         <div class="panel panel-default col-sm-3">
    #                             <div class="panel-heading">Average Power</div>
    #                             <div class="panel-body">{{ result.av_power }}</div>
    #                         </div>
    #                         <div class="panel panel-default col-sm-3">
    #                             <div class="panel-heading">Energy</div>
    #                             <div class="panel-body">{{ result.energy }}</div>
    #                         </div>
    #                     </div>
    #
    #                     <ul class="nav nav-pills">
    #                       <li class="active"><a data-toggle="pill" href="#viz1">Wave significant height Line Chart</a></li>
    #                       <li><a data-toggle="pill" href="#viz2">Power Line Chart</a></li>
    #                       <li><a data-toggle="pill" href="#viz3">Power Histogram</a></li>
    #                     </ul>
    #
    #                     <div class="tab-content">
    #                         <div class="viz_container row tab-pane fade in active"  id="viz1">
    #                             <div class="loadingFrame">
    #                                 <img src="{% static 'img/loading_gif.gif' %}"/>
    #                             </div>
    #                             <iframe src="http://localhost:8000/visualizations/get_line_chart_am/?y_var[]=i0_sea_surface_wave_significant_height&x_var=i0_time&query=313"
    #                                     style="width: 100%; height: 100%; background-color: white;">
    #                             </iframe>
    #                         </div>
    #
    #                         <div class="viz_container row tab-pane fade" id="viz2">
    #                             <div class="loadingFrame">
    #                                 <img src="{% static 'img/loading_gif.gif' %}"/>
    #                             </div>
    #                             <iframe src="http://localhost:8000/visualizations/get_line_chart_am/?y_var[]=power&x_var=i0_time&df=df&notebook_id=2DERXR9WE"
    #                                     style="width: 100%; height: 100%; background-color: white;">
    #                             </iframe>
    #                         </div>
    #
    #                         <div class="viz_container row tab-pane fade" id="viz3">
    #                             <div class="loadingFrame">
    #                                 <img src="{% static 'img/loading_gif.gif' %}"/>
    #                             </div>
    #                             <iframe src="http://localhost:8000/visualizations/get_histogram_chart_am/?y_var[]=power&x_var=power&notebook_id=2DERXR9WE&df=df&bins=15"
    #                                     style="width: 100%; height: 100%; background-color: white;">
    #                             </iframe>
    #                         </div>
    #
    #                     </div>
    #
    #                 </div>
    #             </div>
    #         """)
    #     # print output_html
    #     output_css = textwrap.dedent("""@media screen and (min-width: 768px){.modal:before {display: inline-block;vertical-align: middle;content: " ";height: 100%;}}
    #     .modal-backdrop {z-index:-1;}
    #     #service_result_container{ position: relative; min-height: 500px; width: 100%; /*background-color: white;*/ display: none;}
    #     .loadingDiv, .loadingFrame{position:absolute;z-index:999;display:none;right:0;left:0;bottom:0;top:0;background:#fff;text-align:center;border:thin dashed;}
    #     .viz_container{position: relative; height: 400px; width: 100%; margin: 1% 0;}
    #     #service_result_container iframe{border: none; box-shadow: 0 0 3px 0px #a28e8eb0;}
    #     th{text-align: center; font-weight: 600 !important;}
    #     #service_result_container .nav>li {display: inline-block !important;width: 300px !important; float: none !important;}""")
    #     # print output_css
    #     output_js = textwrap.dedent("""// <script type="text/javascript">
    #     // Get form fields of all the service arguments
    #     $(document).ready(function () {
    #       $.ajax({
    #             url: '/service_builder/load_service_args_form_fields/',
    #             data: {
    #                 service_id: get_service_id()
    #             },
    #             type: 'GET',
    #             success: function(form_fields){
    #                 $("#service_args_container").html(form_fields);
    #             }
    #         });
    #     });
    #
    #
    #
    #
    #
    #     // Submit the service arguments
    #     $("#submitServiceConfig").click(function (element) {
    #       $.ajax({
    #             url: '/service_builder/service/'+get_service_id()+'/execute/',
    #             data: $('#service_args_container').serialize(),
    #             type: 'GET',
    #             beforeSend: function(){
    #                 $("#service_result_container").show();
    #                 $(".loadingDiv").css( "display", "block" );
    #             },
    #             success: function(result){
    #                 $("#service_result_container").html( result );
    #                 // $("iframe").each(function () {
    #                 //     var src = $( this ).attr('data-src');
    #                 //     jQuery.each(result['query_mapping'], function(query, temp_query) {
    #                 //       src = src.replace(new RegExp("query="+query+"&"), "query="+temp_query+"&");
    #                 //       src = src.replace(new RegExp("query="+query+"$"), "query="+temp_query);
    #                 //     });
    #                 //     $( this ).attr({'src': src});
    #                 // });
    #                 $(".loadingDiv").css( "display", "none" );
    #                 $(".loadingFrame").css( "display", "block" );
    #                 $(".viz_container iframe").on( "load", function(){
    #                     $(this).siblings(".loadingFrame").css( "display", "none" )
    #                 });
    #
    #             },
    #             error: function () {
    #                 $(".loadingDiv").css( "display", "none" );
    #                 $("#service_result_container").hide();
    #                 alert('An error occured');
    #             }
    #         });
    #     });
    #         // </script>""")
    #     # print output_js
    #     title = "My test service"
    #     description = "My test description"
    #     price = "free"
    #     private = True
    #
    #     service = Service(user=user)
    #     service.save()
    #
    #     another_user = User(username='another_user_a_zero')
    #     another_user.save()
    #
    #     url = "http://localhost:8000/service_builder/service/" + str(service.id) + "/execute/"
    #     response = cl.get(url)
    #     self.assertEqual(response.status_code, 200)
    #
    #     cl.logout()
    #     cl = Client()
    #     cl.force_login(another_user)
    #     response = cl.get(url)
    #     self.assertEqual(response.status_code, 403)

    def test_access_to_view_dashboard(self):
        dashboardTitle = "A title zero"
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
        cl.logout()
        cl = Client()
        cl.force_login(another_user)

        url = "http://localhost:8000/services/dashboard/" + str(accessible_dashboard_pk) + "/"
        response = cl.post(url)
        self.assertEqual(response.status_code, 403)

        cl.logout()
        cl = Client()
        cl.force_login(user)
        response = cl.post(url)
        self.assertEqual(response.status_code, 200)



    def test_access_to_query(self):
        org_title = 'NESTER'
        org_desc = ''
        organization = Organization(title=org_title, description=org_desc)
        organization.save()
        dataset_name = 'maretec_waves_forecast'
        dataset_title = 'Maretec Waves Forecast'
        temp_now = datetime.now()
        dataset = Dataset(title=dataset_title, stored_at="UBITECH_PRESTO", table_name=dataset_name,
                          organization=organization, temporalCoverageBegin=temp_now, private=True)
        dataset.save()
        dataset_id = dataset.id

        variable_name = 'sea_surface_wave_significant_height'
        variable_title = 'Sea surface wave significant height'
        variable = Variable(name=variable_name, title=variable_title, dataset_id=dataset_id, cell_methods='{}')
        variable.save()
        variable_id = variable.id

        dimension_time_title = 'Time'
        dimension_time_name = 'time'
        dim_time = Dimension(name=dimension_time_name, title=dimension_time_title, variable_id=variable_id)
        dim_time.save()
        dim_time_id = dim_time.id

        dimension_lat_title = 'Latitude'
        dimension_lat_name = 'latitude'
        dim_lat = Dimension(name=dimension_lat_name, title=dimension_lat_title, variable_id=variable_id)
        dim_lat.save()
        dim_lat_id = dim_lat.id

        dimension_lon_title = 'Longitude'
        dimension_lon_name = 'longitude'
        dim_lon = Dimension(name=dimension_lon_name, title=dimension_lon_title, variable_id=variable_id)
        dim_lon.save()
        dim_lon_id = dim_lon.id

        doc_str = {"from":
                       [{"name": dataset_name,
                         "type": str(variable_id),
                         "select": [
                             {"name": "i0_" + variable_name,
                              "type": "VALUE",
                              "title": dataset_title,
                              "exclude": False, "groupBy": False,
                              "aggregate": "AVG"},
                             {"name": "i0_" + str(dimension_time_name),
                              "type": str(dim_time_id),
                              "title": dimension_time_title,
                              "exclude": False,
                              "groupBy": True,
                              "aggregate": "date_trunc_minute"}
                             ,
                             {"name": "i0_" + str(dimension_lat_name),
                              "type": str(dim_lat_id),
                              "title": dimension_lat_title,
                              "exclude": False,
                              "groupBy": True,
                              "aggregate": "round2"},
                             {"name": "i0_" + str(dimension_lon_name),
                              "type": str(dim_lon_id),
                              "title": dimension_lon_title,
                              "exclude": False,
                              "groupBy": True,
                              "aggregate": "round2"}
                         ]}
                        ],
                   "limit": 500,
                   "offset": 0,
                   "filters":
                       {"a": "<" + str(dim_lat_id) + "," + str(dim_lon_id) + ">",
                        "b": "<<30,6>,<46,36>>",
                        "op": "inside_rect"},
                   "distinct": False,
                   "orderings": []
                   }
        user = User(username='testuser_int_a')
        user.save()
        a_q = AbstractQuery(document=doc_str, user=user)
        a_q.save()
        # payload = {"query": doc_str}
        url = "http://localhost:8000/queries/execute/" + str(a_q.id) + "/"
        cl = Client()
        cl.force_login(user)
        response = cl.post(url)
        self.assertEqual(response.status_code, 403)
        dataset.private = False
        dataset.save()
        response = cl.post(url)
        self.assertEqual(response.status_code, 200)