import os

# import the appropriate settings file
if os.environ.get('Production', '') == 'On':
    # production settings
    from bdo_platform.settings_management.production import *
else:
    try:
        # custom settings files
        settings_files = [sf.strip() for sf in
                          open('project//settings_management/settings-loader.txt', 'r').read().split(',')]

        for settings_file in settings_files:
            if settings_file == 'development_dpap':
                from bdo_platform.settings_management.development_dpap import *
            if settings_file == 'development_gtsapelas':
                from bdo_platform.settings_management.development_gtsapelas import *
            elif settings_file == 'development':
                from bdo_platform.settings_management.development import *
    except IOError:
        # default development settings
        from bdo_platform.settings_management.development import *
