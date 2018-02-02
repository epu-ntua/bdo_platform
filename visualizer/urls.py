from django.conf.urls import url
from visualizer import views

urlpatterns = [
    url('^map/$', views.map_viz, name='map-viz'),
    url('^map_index/$', views.MapIndex.as_view(), name='map_index'),
    url('^map_folium/$', views.map_viz_folium, name='map-viz-folium'),
    url('^map_folium_heat/$', views.map_viz_folium_heatmap, name='map-viz-folium'),
    url('^map_heat/$', views.map_heatmap, name='map_heatmap'),
    url('^map_course/$', views.map_course, name='map_course'),
    url('^map_course_time/$', views.map_course_time, name='map_course_time'),

    url('^map_api/$', views.MapAPI.as_view(), name='map_api'),

    url('^map_folium_contour/$', views.map_viz_folium_contour, name='map-viz-folium-contour'),
    url('^map_folium_heat/$', views.map_viz_folium_heatmap, name='map-viz-folium-heat'),

    url('^test_request/$', views.test_request, name='test_request'),
    url('^get_map_simple/$', views.get_map_simple, name='get_map_simple'),
    url('^get_map_contour/$', views.map_viz_folium_contour, name='get_map_contour'),
]
