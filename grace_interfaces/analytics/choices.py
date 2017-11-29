from django.utils.translation import gettext as _
ANALYTIC_OPTIONS =  (
    (0, _("Sentiment Analysis")),
    (1, _("Coding Analysis (Keyword Model)")),
    (2, _("Category Analysis (Similarity Model)")),
    (3, _("Topic Model")),

)

PRESENTATION_SENTIMENT_OPTIONS = (
(0, _("Pie Chart")),
(1, _("Bar Chart")),
)

def options_builder(array):
    OPTIONS = ()
    for i in range(0, len(array)):
        action = (str(i), _(array[i]))
        OPTIONS += (action,)

    return OPTIONS
