from django.db import models


class DownloadedFile(models.Model):
    created_date = models.DateTimeField(auto_now=True)

    year = models.IntegerField()
    percent = models.DecimalField(max_digits=7, decimal_places=2)


class IncomeOutgo(models.Model):
    file = models.ForeignKey(DownloadedFile, on_delete=models.CASCADE)
    row = models.IntegerField()
    income = models.DecimalField(max_digits=16, decimal_places=2)
    outgo = models.DecimalField(max_digits=16, decimal_places=2)
