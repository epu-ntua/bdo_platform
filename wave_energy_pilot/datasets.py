
DATASETS = (
    dict(id="1234", title="Copernicus", variables=(dict(id=1, title="wave_period"),
                                                   dict(id=2, title="wave_height"),
                                                   dict(id=3, title="temperature")),
         min_lat=36.682737, max_lat=37.155939, min_lng=16.676737, max_lng=20.691313, min_date="03/04/2018", max_date="07/05/2018",
         application="wave_forecast"),
    dict(id="2345", title="Maritec - 1", variables=(dict(id=1, title="wave_period"),
                                                       dict(id=2, title="wave_height"),
                                                       dict(id=3, title="temperature")),
             min_lat=-40.98585, max_lat=43.385090, min_lng=-4.215340, max_lng=174.50659, min_date="07/03/2018", max_date="11/03/2018",
         application="wave_resource_assessment_single"),
    dict(id="3456", title="Dummy Name", variables=(dict(id=1, title="wave_period"),
                                                       dict(id=2, title="wave_height"),
                                                       dict(id=3, title="temperature")),
             min_lat=36.346103, max_lat=38.784063, min_lng=-7.114528, max_lng=17.616418, min_date="03/08/2018", max_date="07/09/2018",
         application="wave_resource_assessment_area"),
    dict(id="4567", title="Dataset_4", variables=(dict(id=1, title="wave_period"),
                                                           dict(id=2, title="wave_height"),
                                                           dict(id=3, title="temperature")),
                 min_lat=34.411442, max_lat=35.955777, min_lng=25.391511, max_lng=26.621469, min_date="05/10/2018", max_date="07/11/2018",
         application="data_visualisation"),
    dict(id="5678", title="Dataset_5", variables=(dict(id=1, title="wave_period"),
                                                           dict(id=2, title="wave_height"),
                                                           dict(id=3, title="temperatureeeeeeeeee")),
                 min_lat=42.484251, max_lat=42.484251, min_lng=5.668252, max_lng=5.668252, min_date="03/08/2018", max_date="07/09/2018",
         application="data_visualisation")
)