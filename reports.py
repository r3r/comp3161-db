__author__ = 'RiteshReddy'

import __setup_path
from db import *
from flask_base import *
import datetime


@app.route("/reports/<branch>/topsales")
@validate_branch
def topSalesLaptop(branch):
    laptops = get_laptops_by_top_sales(get_engine(branch))
    print laptops
    return render_template("laptop_top_sales.html", laptops=laptops, branch=branch_titles[branch])


@app.route("/reports/customers", methods=["POST", "GET"])
def customerTotals():
    if request.method == "POST":
        if (request.form.has_key('amount')):
            customers = get_customer_purchase_report_amount(request.form.get('amount', 0))
            if customers == []:
                return render_template("customer_totals.html", customers=customers,
                                       errors="No Customers Found above that threshold.")
            return render_template("customer_totals.html", customers=customers)

        start_date = request.form.get("start_date", datetime.date.today().isoformat())
        end_date = request.form.get("end_date", datetime.date.today().isoformat())
        customers = get_customer_purchase_report_date(start_date, end_date)
        if customers == []:
            return render_template("customer_totals.html", customers=customers,
                                   errors="No Customers found for those dates.")
        return render_template("customer_totals.html", customers=customers)

    else:
        return render_template("customer_totals.html", customers=None)


@app.route("/reports/branches", methods=["POST", "GET"])
def rankedBranches():
    if request.method == "POST":
        start_date = request.form.get("start_date", datetime.date.today().isoformat())
        end_date = request.form.get("end_date", datetime.date.today().isoformat())
        kgn = get_num_sales_branch(get_engine("branch1"), start_date, end_date)
        ochi = get_num_sales_branch(get_engine("branch2"), start_date, end_date)
        mobay = get_num_sales_branch(get_engine("branch3"), start_date, end_date)

        sales = {"branch1": kgn, "branch2": ochi, "branch3": mobay}
        largest = max(sales.items(), key=lambda x: x[1])
        if largest[1] == 0:
            large = "abcdef"
        else:
            large = largest[0]
        return render_template("branch_totals.html", largest=large, **sales)
    else:
        return render_template("branch_totals.html", largest=None)
