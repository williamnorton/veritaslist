from django.contrib import admin
from beta.models import List, Choice, ChoiceGroup

# Register your models here.
admin.site.register(List)
admin.site.register(Choice)
admin.site.register(ChoiceGroup)
