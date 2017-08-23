SERVICE_TYPES = [
    # {
    #     'id': 'on_demand',
    #     'icon': 'life-saver',
    #     'title': 'On demand',
    #     'color': 'orange',
    # },
    {
        'id': 'dataset',
        'icon': 'database',
        'title': 'Dataset',
        'color': 'blue',
    },
    {
        'id': 'analysis',
        'icon': 'industry',
        'title': 'Analysis',
        'color': 'red',
    },
    {
        'id': 'analysis',
        'icon': 'industry',
        'title': 'Analysis',
        'color': 'red',
    },
]

SERVICE_TYPES_CHOICES = [
    (s['id'], s['title']) for s in SERVICE_TYPES
]
