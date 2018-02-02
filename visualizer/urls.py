from django.conf.urls import url
from visualizer import views

urlpatterns = [
    url('^map/$', views.map_viz, name='map-viz'),
    url('^map_folium_contour/$', views.map_viz_folium_contour, name='map-viz-folium-contour'),
    url('^map_folium_heat/$', views.map_viz_folium_heatmap, name='map-viz-folium-heat'),

    url('^test_request/$', views.test_request, name='test_request'),
    url('^test_request_zep/$', views.test_request_zep, name='test_request_zep'),
    url('^get_map_simple/$', views.get_map_simple, name='get_map_simple'),
    url('^get_map_contour/$', views.map_viz_folium_contour, name='get_map_contour'),

    url('^get_pie_chart/$', views.get_pie_chart, name='get_pie_chart'),
    url('^get_line_chart/$', views.get_line_chart, name='get_line_chart'),

    url('^get_table_zep/$', views.get_table_zep, name='get_table_zep'),
    url('^get_line_chart_zep/$', views.get_line_chart_zep, name='get_line_chart_zep'),
    url('^get_bar_chart_zep/$', views.get_bar_chart_zep, name='get_bar_chart_zep'),
    url('^get_pie_chart_zep/$', views.get_pie_chart_zep, name='get_pie_chart_zep'),
    url('^get_area_chart_zep/$', views.get_area_chart_zep, name='get_area_chart_zep'),
    url('^get_scatter_chart_zep/$', views.get_scatter_chart_zep, name='get_scatter_chart_zep'),

    url('^get_line_chart_am/$', views.get_line_chart_am, name='get_line_chart_am'),
    url('^get_pie_chart_am/$', views.get_pie_chart_am, name='get_pie_chart_am'),
    url('^get_column_chart_am/$', views.get_column_chart_am, name='get_column_chart_am'),

    url('^get_data_table/$', views.get_data_table, name='get_data_table'),

]
