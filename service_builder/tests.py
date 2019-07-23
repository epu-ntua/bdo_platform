from django.test import TestCase
from models import Service
import json
from django.test import Client
import textwrap
from django.contrib.auth.models import User


# Create your tests here.
class ServiceBuilderTest(TestCase):
    def test_service_creation(self):
        user = User(username='testuser_s')
        user.save()
        cl = Client()
        cl.force_login(user)
        selected_queries_dict = {"Q1": {"query_id": "313", "paragraphs": ["20180501-135246_1102090558"]}}
        selected_queries = json.dumps(selected_queries_dict)
        # print selected_queries
        arguments_dict = {"filter-arguments": [
            {"default_lat_max": "42.098", "areaSelectHeight": "100", "name": "area_select", "areaSelectWidth": "150",
             "title": "Select the area", "default": "<<35.675,-12.744>,<42.098,-1.846>>", "default_lat_min": "35.675",
             "filter_op": " inside_rect", "default_lon_min": "-12.744", "default_lon_max": "-1.846", "query": "Q1",
             "type": "SPATIAL_COV", "filter_b": "<<35.675,-12.744>,<42.098,-1.846>>", "filter_a": "<36,38>"},
            {"name": "start_date", "title": "Starting Date", "default": "2018-01-01 00:00", "filter_op": "gte",
             "query": "Q1", "type": "DATETIME", "filter_b": "2018-01-01 00:00", "filter_a": "i0_time"},
            {"name": "end_date", "title": "Ending Date", "default": "2018-01-31 00:00", "filter_op": "lte",
             "query": "Q1", "type": "DATETIME", "filter_b": "2018-01-31 00:00", "filter_a": "i0_time"}],
                          "algorithm-arguments": []}
        arguments = json.dumps(arguments_dict)
        # print arguments
        notebook_id = "2DP3SVY7D"
        # print notebook_id
        output_html = textwrap.dedent(
            """<div id="service_container" class="text-center">
                    <div id="service_config_container" class="text-center">
                        <button type="button" id="argsCollapseBtn" class="btn btn-md btn-primary" data-toggle="collapse" data-target="#serviceConfigCollapse">
                          Configure
                        </button>
                        <div id="serviceConfigCollapse" class="collapse in" >
                            <div class="well">
                                <h4 class="modal-title">Please give your input</h4>
                                <form id="service_args_container" class="modal-body" style="padding: 0 25%">

                                </form>
                                <button type="button" class="btn btn-success" data-toggle="collapse" data-target="#serviceConfigCollapse" id="submitServiceConfig">Submit</button>
                                <button type="button" class="btn btn-default" data-toggle="collapse" data-target="#serviceConfigCollapse">Cancel</button>
                            </div>
                        </div>
                    </div>

                    <div id="service_result_container" class="text-center">
                        {% load static %}
                        <div class="loadingDiv">
                            <img src="http://assets.motherjones.com/interactives/projects/features/koch-network/shell19/img/loading.gif"/>
                        </div>

                        <table class="table table-full-width">
                            <thead>
                                <tr>
                                    <th>Maximum Height</th><th>Average Height</th><th>Standard Deviation</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>{{ result.max_height }}</td><td>{{ result.av_height }}</td><td>{{ result.stand_dev_height }}</td>
                                </tr>
                            </tbody>
                        </table>

                        <table class="table table-full-width">
                            <thead>
                                <tr>
                                    <th>Maximum Period</th><th>Average Period</th><th>Standard Deviation</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>{{ result.max_period }}</td><td>{{ result.av_period }}</td><td>{{ result.stand_dev_period }}</td>
                                </tr>
                            </tbody>
                        </table>

                        <div class="panel-group row">
                            <div class="panel panel-default col-sm-3">
                                <div class="panel-heading">Maximum Power</div>
                                <div class="panel-body">{{ result.max_power }}</div>
                            </div>
                            <div class="panel panel-default col-sm-3">
                                <div class="panel-heading">Minimum Power</div>
                                <div class="panel-body">{{ result.min_power }}</div>
                            </div>
                            <div class="panel panel-default col-sm-3">
                                <div class="panel-heading">Average Power</div>
                                <div class="panel-body">{{ result.av_power }}</div>
                            </div>
                            <div class="panel panel-default col-sm-3">
                                <div class="panel-heading">Energy</div>
                                <div class="panel-body">{{ result.energy }}</div>
                            </div>
                        </div>

                        <ul class="nav nav-pills">
                          <li class="active"><a data-toggle="pill" href="#viz1">Wave significant height Line Chart</a></li>
                          <li><a data-toggle="pill" href="#viz2">Power Line Chart</a></li>
                          <li><a data-toggle="pill" href="#viz3">Power Histogram</a></li>
                        </ul>

                        <div class="tab-content">
                            <div class="viz_container row tab-pane fade in active"  id="viz1">
                                <div class="loadingFrame">
                                    <img src="{% static 'img/loading_gif.gif' %}"/>
                                </div>
                                <iframe src="http://localhost:8000/visualizations/get_line_chart_am/?y_var[]=i0_sea_surface_wave_significant_height&x_var=i0_time&query=313"
                                        style="width: 100%; height: 100%; background-color: white;">
                                </iframe>
                            </div>

                            <div class="viz_container row tab-pane fade" id="viz2">
                                <div class="loadingFrame">
                                    <img src="{% static 'img/loading_gif.gif' %}"/>
                                </div>
                                <iframe src="http://localhost:8000/visualizations/get_line_chart_am/?y_var[]=power&x_var=i0_time&df=df&notebook_id=2DERXR9WE"
                                        style="width: 100%; height: 100%; background-color: white;">
                                </iframe>
                            </div>

                            <div class="viz_container row tab-pane fade" id="viz3">
                                <div class="loadingFrame">
                                    <img src="{% static 'img/loading_gif.gif' %}"/>
                                </div>
                                <iframe src="http://localhost:8000/visualizations/get_histogram_chart_am/?y_var[]=power&x_var=power&notebook_id=2DERXR9WE&df=df&bins=15"
                                        style="width: 100%; height: 100%; background-color: white;">
                                </iframe>
                            </div>

                        </div>

                    </div>
                </div>
            """)
        # print output_html
        output_css = textwrap.dedent("""@media screen and (min-width: 768px){.modal:before {display: inline-block;vertical-align: middle;content: " ";height: 100%;}}
.modal-backdrop {z-index:-1;}
#service_result_container{ position: relative; min-height: 500px; width: 100%; /*background-color: white;*/ display: none;}
.loadingDiv, .loadingFrame{position:absolute;z-index:999;display:none;right:0;left:0;bottom:0;top:0;background:#fff;text-align:center;border:thin dashed;}
.viz_container{position: relative; height: 400px; width: 100%; margin: 1% 0;}
#service_result_container iframe{border: none; box-shadow: 0 0 3px 0px #a28e8eb0;}
th{text-align: center; font-weight: 600 !important;}
#service_result_container .nav>li {display: inline-block !important;width: 300px !important; float: none !important;}""")
        # print output_css
        output_js = textwrap.dedent("""// <script type="text/javascript">
// Get form fields of all the service arguments
$(document).ready(function () {
  $.ajax({
        url: '/service_builder/load_service_args_form_fields/',
        data: {
            service_id: get_service_id()
        },
        type: 'GET',
        success: function(form_fields){
            $("#service_args_container").html(form_fields);
        }
    });
});





// Submit the service arguments
$("#submitServiceConfig").click(function (element) {
  $.ajax({
        url: '/service_builder/service/'+get_service_id()+'/execute/',
        data: $('#service_args_container').serialize(),
        type: 'GET',
        beforeSend: function(){
            $("#service_result_container").show();
            $(".loadingDiv").css( "display", "block" );
        },
        success: function(result){
            $("#service_result_container").html( result );
            // $("iframe").each(function () {
            //     var src = $( this ).attr('data-src');
            //     jQuery.each(result['query_mapping'], function(query, temp_query) {
            //       src = src.replace(new RegExp("query="+query+"&"), "query="+temp_query+"&");
            //       src = src.replace(new RegExp("query="+query+"$"), "query="+temp_query);
            //     });
            //     $( this ).attr({'src': src});
            // });
            $(".loadingDiv").css( "display", "none" );
            $(".loadingFrame").css( "display", "block" );
            $(".viz_container iframe").on( "load", function(){
                $(this).siblings(".loadingFrame").css( "display", "none" )
            });

        },
        error: function () {
            $(".loadingDiv").css( "display", "none" );
            $("#service_result_container").hide();
            alert('An error occured');
        }
    });
});
    // </script>""")
        # print output_js
        title = "My test service"
        description = "My test description"
        price = "free"
        private = True

        service = Service(user=user)
        service.save()
        service_id = service.id

        payload = {"selected_queries": selected_queries,
                   "exposed_args": arguments,
                   "notebook_id": notebook_id,
                   "output_html": output_html,
                   "output_css": output_css,
                   "output_js": output_js,
                   "title": str(title),
                   "description": description,
                   "price": price,
                   "private": private,
                   "service_id": service_id}

        url = "http://localhost:8000/service_builder/publish/"

        cl.post(url, payload)

        service = Service.objects.get(pk=service_id)

        self.assertEqual(str(service.title), str(title))
        self.assertEqual(service.private, private)
        self.assertEqual(service.published, True)
        self.assertEqual(service.price, price)
        self.assertEqual(service.description, description)
        self.assertEqual(service.notebook_id, notebook_id)
        self.assertEqual(service.output_html, output_html)
        self.assertEqual(service.output_css, output_css)
        self.assertEqual(service.output_js, output_js)
        self.assertDictEqual(service.arguments, arguments_dict)
        self.assertEqual(service.queries, selected_queries_dict)
