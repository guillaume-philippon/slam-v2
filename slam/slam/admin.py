from django.contrib import admin

class SlamAdminSite(admin.AdminSite):
    final_catch_all_view = True
