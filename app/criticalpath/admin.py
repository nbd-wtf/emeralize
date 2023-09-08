from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Journey)
admin.site.register(Category)
# admin.site.register(Phase)
admin.site.register(Resource)
admin.site.register(Workshop)
# admin.site.register(ResourceAdditive)
admin.site.register(Comment)
admin.site.register(Fav)
admin.site.register(JourneyResources)
admin.site.register(Reward)
admin.site.register(Course)
admin.site.register(CourseResources)
admin.site.register(CoursePaymentSplits)
admin.site.register(Ebook)
admin.site.register(EbookPaymentSplits)

# @admin.register(Resource)
# class ResourceAdmin(admin.ModelAdmin):
#     pass