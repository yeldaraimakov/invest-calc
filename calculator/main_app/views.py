from django.template.loader import render_to_string
from django.http import HttpResponse

from weasyprint import HTML

from .models import DownloadedFile, IncomeOutgo


def download(request):
    percent = float(request.POST.get('percent', 0))
    year = int(request.POST.get('year', 1))

    incomes = []
    outgos = []

    for i in range(1, year+1):
        incomes.append(float(request.POST.get('income_' + str(i), 0)))
        outgos.append(float(request.POST.get('outgo_' + str(i), 0)))

    save_datas(incomes, outgos, percent, year)

    html_template = render_to_string('main_app/home_pdf.html',
                                     context=get_calculated_datas(incomes, outgos, percent, year))

    pdf_file = HTML(string=html_template).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="npv.pdf"'
    return response


def get_calculated_datas(incomes, outgos, percent, year):
    coefs = []
    discounteds = []

    totalOutgo = 0
    totalIncome = 0
    totalRes = 0
    totalDiscounted = 0
    c0 = 0

    for i, income in enumerate(incomes):
        outgo = outgos[i]
        res = income - outgo
        coef = 1 / (1 + percent / 100) ** i
        discounted = res * coef

        coefs.append(coef)
        discounteds.append(discounted)

        totalIncome += income
        totalOutgo += outgo
        totalRes += res

        if i == 0:
            c0 = outgo
        else:
            totalDiscounted += discounted

    profIndex = c0 != 0 and totalDiscounted / c0 or '∞'
    totalDiscounted -= c0

    return {'incomes': incomes, 'outgos': outgos, 'coefs': coefs,
            'discounteds': discounteds, 'percent': percent, 'year': year,
            'totalIncome': totalIncome, 'totalOutgo': totalOutgo,
            'totalRes': totalRes,
            'totalDiscounted': totalDiscounted, 'profIndex': profIndex}


def save_datas(incomes, outgos, percent, year):

    file = DownloadedFile.objects.create(percent=percent, year=year)

    for i, income in enumerate(incomes):
        IncomeOutgo.objects.create(income=income, outgo=outgos[i], file=file, row=i)

