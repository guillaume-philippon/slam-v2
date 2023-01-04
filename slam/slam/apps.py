from django.contrib.admin.apps import  AdminConfig

class SlamAdminConfig(AdminConfig):
    default_site = 'slam.admin.SlamAdminSite'
