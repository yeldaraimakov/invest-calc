from django.contrib import admin

from .models import DownloadedFile, IncomeOutgo

admin.site.register([DownloadedFile, IncomeOutgo])
