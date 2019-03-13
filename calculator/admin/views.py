from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from calculator.main_app.models import DownloadedFile, IncomeOutgo
from calculator.main_app.views import get_calculated_datas


@method_decorator([login_required], name='dispatch')
class FilesListView(ListView):
    model = DownloadedFile
    template_name = "admin/files_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        files = DownloadedFile.objects.all().order_by('-created_date')

        for file in files:
            income_outgos = IncomeOutgo.objects.filter(file=file)

            incomes = []
            outgos = []

            for income_outgo in income_outgos:
                incomes.append(income_outgo.income)
                outgos.append(income_outgo.outgo)

            file.data = get_calculated_datas(incomes, outgos, file.percent, file.year)

        context['files'] = files

        return context
