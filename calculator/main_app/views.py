import xlwt
import json
import random

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import FormView

from .models import DownloadedFile, IncomeOutgo, User
from .forms import RegistrationForm
from .helpers import get_calculated_datas, calc_npv


def download_excel(request):
    percent = float(request.POST.get('percent', 0))
    year = int(request.POST.get('year', 1))
    project_name = request.POST.get('project_name', '')
    irr = request.POST.get('irr', 0)

    if not project_name:
        project_name = 'New Project ' + str(random.randint(1, 1000))

    incomes = []
    outgos = []

    for i in range(1, year + 1):
        incomes.append(float(request.POST.get('income_' + str(i), 0)))
        outgos.append(float(request.POST.get('outgo_' + str(i), 0)))

    user = None if request.user.is_anonymous else request.user
    print(user)

    save_datas(incomes, outgos, percent, year, user, project_name, irr)

    ctx = get_calculated_datas(incomes, outgos, percent, year)

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="' + project_name + '-NPV-calc.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    ws.write(0, 0, 'Ставка дисконтирования', font_style)
    ws.write(0, 1, percent, font_style)
    ws.write(0, 3, 'Срок', font_style)
    ws.write(0, 4, year, font_style)

    ws.write(2, 0, 'ЧДД/NPV', font_style)
    ws.write(2, 1, float(ctx.get('totalDiscounted')), font_style)
    ws.write(2, 3, 'Индекс прибыльности', font_style)
    ws.write(2, 4, ctx.get('profIndex'), font_style)

    columns = ['Год', 'Доходы проекта', 'Первоначальные инвестиции/Расходы проекта',
               'Чистый поток платежей', 'Коэффициент дисконтирования', 'Дисконтированные платежи']

    for col_num in range(len(columns)):
        ws.write(4, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    for row_num in range(len(incomes)):
        ws.write(row_num + 5, 0, row_num, font_style)
        ws.write(row_num + 5, 1, incomes[row_num], font_style)
        ws.write(row_num + 5, 2, outgos[row_num], font_style)
        ws.write(row_num + 5, 3, incomes[row_num] - outgos[row_num], font_style)
        ws.write(row_num + 5, 4, ctx.get('coefs')[row_num], font_style)
        ws.write(row_num + 5, 5, ctx.get('discounteds')[row_num], font_style)

    row_num = len(incomes) + 5
    ws.write(row_num, 0, 'Итого', font_style)
    ws.write(row_num, 1, ctx.get('totalIncome'), font_style)
    ws.write(row_num, 2, ctx.get('totalOutgo'), font_style)
    ws.write(row_num, 3, ctx.get('totalRes'), font_style)

    wb.save(response)
    return response


def save_datas(incomes, outgos, percent, year, user, project_name, irr):
    file = DownloadedFile.objects.create(percent=percent, year=year, user=user, project_name=project_name, irr=irr)

    for i, income in enumerate(incomes):
        IncomeOutgo.objects.create(income=income, outgo=outgos[i], file=file, row=i)


def user_login(request):
    current_user = request.user
    if current_user and current_user.id:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.role == User.ADMIN:
                return redirect('admin_home')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Неверные учетные данные')
            return render(request, 'main_app/login.html')

    return render(request, 'main_app/login.html')


def user_logout(request):
    logout(request)
    return redirect('home')


@login_required(login_url='/login')
def charts(request):
    user = request.user
    if user.role != User.INVESTOR:
        return HttpResponse('Не положено', status=403)

    files = DownloadedFile.objects.filter(user=user)

    json_list = []

    for file in files:
        income_outgos = IncomeOutgo.objects.filter(file=file)

        incomes = []
        outgos = []

        for income_outgo in income_outgos:
            incomes.append(income_outgo.income)
            outgos.append(income_outgo.outgo)

        npvs = {}

        for percent in range(0, 100, 5):
            npv = calc_npv(file.year, percent, incomes, outgos)
            npvs.update({percent: npv})

        json_list.append({'npvs': npvs, 'project_name': file.project_name,
                          'npv': calc_npv(file.year, file.percent, incomes, outgos), 'irr': file.irr})

    percents = [percent for percent in range(0, 100, 5)]

    return render(request, 'main_app/charts.html', context={'datas': json.dumps(json_list), 'percents': json.dumps(percents)})


class RegistrationFormView(FormView):
    form_class = RegistrationForm
    template_name = 'main_app/registration.html'

    def form_valid(self, form):
        form.save(commit=True)
        messages.success(self.request, "Регистрация успешно выполнена")
        return redirect('user_login')
