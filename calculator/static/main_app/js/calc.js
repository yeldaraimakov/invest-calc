$(document).ready(function() {
    $("#year").on("change", function() {
        var year = parseInt($('#year').val());
        for (var i = 1; i <= year; ++i) {
            $('#row_' + i).show();
            $('#row_pp_' + i).show();
            $('#row_dpp_' + i).show();
        }
        for (i = year + 1; i < 11; ++i) {
            $('#row_' + i).hide();
            $('#row_pp_' + i).hide();
            $('#row_dpp_' + i).hide();
        }
        recalc();
    });

    function recalc() {
        recalcNPV();
        recalcPP();
        recalcDPP();
        recalcIRR();
    }

    function recalcNPV() {
        var year = parseInt($('#year').val());
        var percent = parseFloat($('#percent').val());
        var totalOutgo = 0;
        var totalIncome = 0;
        var totalRes = 0;
        var totalDiscounted = 0;
        var c0 = 0;
        for (var i = 1; i <= year; ++i) {
            var income = i > 1 ? parseInt($('#col_1_' + i).val()) : 0;
            var outgo = parseInt($('#col_2_' + i).val());
            var res = income - outgo;
            $('#col_3_' + i).html(res);

            var coef = 1 / Math.pow(1 + percent / 100, i - 1);
            $('#col_4_' + i).html(coef.toFixed(2));

            var discounted = res * coef;
            $('#col_5_' + i).html(discounted.toFixed(2));

            totalIncome += income;
            totalOutgo += outgo;
            totalRes += res;

            if (i === 1) {
                c0 = outgo;
            } else {
                totalDiscounted += discounted;
            }
        }
        $('#totalIncome').html(totalIncome);
        $('#totalOutgo').html(totalOutgo);
        $('#totalRes').html(totalRes);
        $('#totalDiscounted').html((totalDiscounted - c0).toFixed(2));
        if (c0 !== 0) {
            $('#profIndex').html((totalDiscounted / c0).toFixed(2));
        } else {
            $('#profIndex').html('∞');
        }

        // recalc ARR
        var incomeCP = totalIncome / (year - 1);
        var arr = incomeCP * 100 / totalOutgo;
        $('#arr').html(arr.toFixed(2));
        $('#arr-input').val(arr.toFixed(2));
    }

    function recalcIRR() {
        var l = 0, r = 100;
        var eps = 0.001;
        var ans = -1;
        while (Math.abs(r - l) > eps) {
            var percent = (l + r) / 2;
            var year = parseInt($('#year').val());
            var totalDiscounted = 0;
            var c0 = 0;
            for (var i = 1; i <= year; ++i) {
                var income = i > 1 ? parseInt($('#col_1_' + i).val()) : 0;
                var outgo = parseInt($('#col_2_' + i).val());
                var res = income - outgo;
                var coef = 1 / Math.pow(1 + percent / 100, i - 1);
                var discounted = res * coef;

                if (i === 1) {
                    c0 = outgo;
                } else {
                    totalDiscounted += discounted;
                }
            }
            if (totalDiscounted - c0 > 0) {
                l = percent;
            } else {
                r = percent;
            }
            ans = totalDiscounted - c0;
        }
        if (ans < eps) {
            $('#irr').html(l.toFixed(2));
            $('#irr-input').val(l.toFixed(2));
        } else {
            $('#irr').html('not found (between 0 and 100)');
            $('#irr-input').val('not found (between 0 and 100)');
        }
    }

    function recalcPP() {
        var year = parseInt($('#year').val());
        var totalRes = 0;
        var totalOutgo = 0;
        var ppNotFound = true;
        var pp = -1;
        for (var i = 1; i <= year; ++i) {
            var income = i > 1 ? parseInt($('#col_1_' + i).val()) : 0;
            var outgo = parseInt($('#col_2_' + i).val());
            var res = income - outgo;

            totalOutgo += outgo;
            totalRes += res;

            if (totalRes >= 0 && ppNotFound) {
                ppNotFound = false;
                pp = i;
            }

            $('#pp_col_1_' + i).html(totalOutgo);
            $('#pp_col_2_' + i).html(totalRes);
        }
        if (pp === -1) {
            $('#pp').html(' > ' + year);
            $('#pp-input').val(' > ' + year);
        } else {
            $('#pp').html(pp);
            $('#pp-input').val(pp);
        }
    }

    function recalcDPP() {
        var year = parseInt($('#year').val());
        var totalDiscounted = 0;
        var totalOutgo = 0;
        var dppNotFound = true;
        var dpp = -1;
        for (var i = 1; i <= year; ++i) {
            var outgo = parseInt($('#col_2_' + i).val());
            var discounted = parseFloat($('#col_5_' + i).html());

            totalOutgo += outgo;
            totalDiscounted += discounted;

            if (totalDiscounted >= 0 && dppNotFound) {
                dppNotFound = false;
                dpp = i;
            }

            $('#dpp_col_1_' + i).html(totalOutgo);
            $('#dpp_col_2_' + i).html(totalDiscounted.toFixed(2));
        }
        if (dpp === -1) {
            $('#dpp').html(' > ' + year);
            $('#dpp-input').val(' > ' + year);
        } else {
            $('#dpp').html(dpp);
            $('#dpp-input').val(dpp);
        }
    }

    document.getElementById('percent').addEventListener('input', function () {
        recalc();
    });

    for (var i = 2; i < 11; ++i) {
        document.getElementById('col_1_' + i).addEventListener('input', function () {
            recalc();
        });
    }

    for (i = 1; i < 11; ++i) {
        document.getElementById('col_2_' + i).addEventListener('input', function () {
            recalc();
        });
    }

    $("#cleanBtn").click(function() {
        for (var i = 1; i < 11; ++i) {
            $('#col_1_' + i).val(0);
            $('#col_2_' + i).val(0);
        }
        recalc();
    });
});