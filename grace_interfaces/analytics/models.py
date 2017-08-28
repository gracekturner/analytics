from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# properties include analytic model type, presentation type, data set id, etc.
# e.g. a dataset id Property would look like:
#title = Dataset_ownerID
#description = "'excelfilename'_'sheetname'_'text_column'"
# analytic descriptive property would be:
#title = KeywordModel_123232_dict
#description = "{"data": 1, "dataset": 2, "datahundred": 3}"
# but an analytic descriptive category attached to a text would be:
#title = KeywordModel_123232
#description = "1" (meaning in that text "data" alone was found)



class Property(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

# piece of text with associated properties.
class Text(models.Model):
    text = models.TextField()
    properties = models.ManyToManyField(Property)

#eventually create a user database
#class Users(models)
