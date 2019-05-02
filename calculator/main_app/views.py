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
    arr = request.POST.get('arr', 0)
    pp = request.POST.get('pp', 0)
    dpp = request.POST.get('dpp', 0)

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
    header_font = xlwt.XFStyle()
    header_font.font.bold = True

    # Sheet body, remaining rows
    body_font = xlwt.XFStyle()

    ws.write(0, 0, 'Ставка дисконтирования', header_font)
    ws.write(0, 1, percent, header_font)
    ws.write(0, 3, 'Срок', header_font)
    ws.write(0, 4, year, header_font)

    ws.write(2, 0, 'ЧДД/NPV', header_font)
    ws.write(2, 1, float(ctx.get('totalDiscounted')), header_font)
    ws.write(3, 0, 'Индекс прибыльности', header_font)
    ws.write(3, 1, ctx.get('profIndex'), header_font)
    ws.write(4, 0, 'IRR (внутренняя ставка доходности)', header_font)
    ws.write(4, 1, irr, header_font)
    ws.write(2, 3, 'ARR (рентабельность инвестиционного проекта)', header_font)
    ws.write(2, 4, arr, header_font)
    ws.write(3, 3, 'PP (срок окупаемости проекта)', header_font)
    ws.write(3, 4, pp, header_font)
    ws.write(4, 3, 'DPP(дисконтированный срок окупаемости)', header_font)
    ws.write(4, 4, dpp, header_font)

    # npv table
    ws.write(6, 0, 'NPV (чистая приведенная стоимость)', header_font)
    columns = ['Год', 'Доходы проекта', 'Первоначальные инвестиции/Расходы проекта',
               'Чистый поток платежей', 'Коэффициент дисконтирования', 'Дисконтированные платежи']

    for col_num in range(len(columns)):
        ws.write(7, col_num, columns[col_num], header_font)

    for row_num in range(len(incomes)):
        ws.write(row_num + 8, 0, row_num, body_font)
        ws.write(row_num + 8, 1, incomes[row_num], body_font)
        ws.write(row_num + 8, 2, outgos[row_num], body_font)
        ws.write(row_num + 8, 3, incomes[row_num] - outgos[row_num], body_font)
        ws.write(row_num + 8, 4, ctx.get('coefs')[row_num], body_font)
        ws.write(row_num + 8, 5, ctx.get('discounteds')[row_num], body_font)

    row_num = len(incomes) + 8
    ws.write(row_num, 0, 'Итого', body_font)
    ws.write(row_num, 1, ctx.get('totalIncome'), body_font)
    ws.write(row_num, 2, ctx.get('totalOutgo'), body_font)
    ws.write(row_num, 3, ctx.get('totalRes'), body_font)

    # pp table
    ws.write(row_num + 2, 0, 'DPP (дисконтированный срок окупаемости)', header_font)
    row_num += 3
    ws.write(row_num, 0, 'Год', header_font)
    ws.write(row_num, 1, 'Первоначальные затраты', header_font)
    ws.write(row_num, 2, 'Денежный поток нарастающим итогом', header_font)

    total_res = 0
    total_outgo = 0
    for i in range(len(incomes)):
        total_res += incomes[i] - outgos[i]
        total_outgo += outgos[i]
        ws.write(row_num + i + 1, 0, i, body_font)
        ws.write(row_num + i + 1, 1, total_outgo, body_font)
        ws.write(row_num + i + 1, 2, total_res, body_font)

    # dpp table
    row_num += len(incomes) + 3
    ws.write(row_num - 1, 0, 'DPP (дисконтированный срок окупаемости)', header_font)
    ws.write(row_num, 0, 'Год', header_font)
    ws.write(row_num, 1, 'Первоначальные затраты', header_font)
    ws.write(row_num, 2, 'Дисконтированный поток нарастающим потоком', header_font)

    total_outgo = 0
    total_discounted = 0
    for i in range(len(incomes)):
        total_outgo += outgos[i]
        total_discounted += ctx.get('discounteds')[i]

        ws.write(row_num + i + 1, 0, i, body_font)
        ws.write(row_num + i + 1, 1, total_outgo, body_font)
        ws.write(row_num + i + 1, 2, total_discounted, body_font)

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
        print(email, password)
        user = authenticate(request, email=email, password=password)
        print(user)
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

    return render(request, 'main_app/charts.html', context={'datas': json.dumps(json_list),
                                                            'percents': json.dumps(percents), 'is_empty': not files})


class RegistrationFormView(FormView):
    form_class = RegistrationForm
    template_name = 'main_app/registration.html'

    def form_valid(self, form):
        form.save(commit=True)
        messages.success(self.request, "Регистрация успешно выполнена")
        return redirect('user_login')
