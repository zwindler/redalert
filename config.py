class Config(object):
    DEBUG = False
    SEVERITY_LEVELS = [
        {
            "label": "Severity 1",
            "value": "sev1"
        },
        {
            "label": "Severity 2",
            "value": "sev2"
        },
        {
            "label": "Severity 3",
            "value": "sev3"
        },
        {
            "label": "Severity 4",
            "value": "sev4"
        },
        {
            "label": "Severity 5",
            "value": "sev5"
        }
    ]
    INCLUDE_IN_INCIDENT = {
        "always" : [],
        "sev1" : [],
        "sev2" : [],
        "sev3" : [],
        "sev4" : [],
        "sev5" : []
    }
