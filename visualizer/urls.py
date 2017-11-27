from django.conf.urls import url
from visualizer import views

urlpatterns = [
    # base analytics
    url('^map/$', views.map_viz, name='map-viz'),
    url('^map_index/$', views.MapIndex.as_view(), name='map_index'),
    url('^map_folium/$', views.map_viz_folium, name='map-viz-folium'),
    url('^map_folium_heat/$', views.map_viz_folium_heatmap, name='map-viz-folium'),
    url('^map_heat/$', views.map_heatmap, name='map_heatmap'),

    url('^map_api/$', views.MapAPI.as_view(), name='map_api'),

]
