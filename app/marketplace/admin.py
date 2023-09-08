from django.contrib import admin

# Register your models here.
from .models import FeaturedWorkshops, FeaturedEbooks, FeaturedCreators, UserProfile, Charge, Purchase, Transaction, TransactionCode, TransactionType, Wallet, Withdrawal, FeaturedCourses, Currency

admin.site.register(Charge)
admin.site.register(Purchase)
admin.site.register(Transaction)
admin.site.register(TransactionCode)
admin.site.register(Wallet)
admin.site.register(Withdrawal)
admin.site.register(TransactionType)
admin.site.register(UserProfile)
admin.site.register(FeaturedCreators)
admin.site.register(FeaturedCourses)
admin.site.register(FeaturedEbooks)
admin.site.register(FeaturedWorkshops)
admin.site.register(Currency)