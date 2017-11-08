from django.conf.urls import url
from visualizer import views

urlpatterns = [
    # base analytics
    url('^map/$', views.map_viz, name='map-viz'),
    url('^map_folium/$', views.map_viz_folium, name='map-viz-folium'),
    url('^map_folium_contour/$', views.map_viz_folium_contour, name='map-viz-folium-contour'),
    url('^map_folium_colormesh/$', views.map_viz_folium_colormesh, name='map-viz-folium-colormesh'),
    url('^map_folium_heat/$', views.map_viz_folium_heatmap, name='map-viz-folium-heat'),
    url('^map_folium_colormap/$', views.map_viz_folium_colormap, name='map-viz-folium-colormap'),
]
