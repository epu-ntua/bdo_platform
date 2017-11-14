from django.conf.urls import url
from visualizer import views

urlpatterns = [
    url('^map/$', views.map_viz, name='map-viz'),
    url('^map_folium/$', views.map_viz_folium, name='map-viz-folium'),
    url('^map_folium_contour/$', views.map_viz_folium_contour, name='map-viz-folium-contour'),
    url('^map_folium_heat/$', views.map_viz_folium_heatmap, name='map-viz-folium-heat'),

    url('^test_request/$', views.test_request, name='test_request'),
    url('^get_map_simple/$', views.get_map_simple, name='get_map_simple'),
    url('^get_map_contour/$', views.map_viz_folium_contour, name='get_map_contour'),
]
