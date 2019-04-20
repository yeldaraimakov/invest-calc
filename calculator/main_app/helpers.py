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


def calc_npv(year, percent, incomes, outgos):
    c0, total_discounted = 0, 0

    for i in range(year):
        coef = float(1 / (1 + percent / 100) ** i)
        discounted = float(incomes[i] - outgos[i]) * coef

        if i == 0:
            c0 = outgos[i]
        else:
            total_discounted += discounted

    return float(total_discounted) - float(c0)
