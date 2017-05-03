# Copyright (c) 2013, Selco and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.hr.doctype.process_payroll.process_payroll import get_month_details
from frappe import msgprint
import datetime
from datetime import timedelta
from frappe.utils import cint, flt, nowdate,getdate
from frappe import msgprint
from operator import add

def execute(filters=None):
    columns, data = [], []
    columns = get_columns()
    data = get_lead_details(filters)
    return columns, data

def get_lead_details(filters):
    msd = "0000/00/00"
    med = "0000/00/00"
    fiscal_year = filters.get("fiscal_year")
    if filters.get("fiscal_year"):
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
            "Dec"].index(filters["month_number"]) + 1
        ysd = frappe.db.get_value("Fiscal Year", fiscal_year, "year_start_date")
        #frappe.msgprint(ysd)
        from dateutil.relativedelta import relativedelta
        import calendar, datetime
        diff_mnt = cint(month)-cint(ysd.month)
        if diff_mnt<0:
            diff_mnt = 12-int(ysd.month)+cint(month)
        msd = ysd + relativedelta(months=diff_mnt) # month start date
        month_days = cint(calendar.monthrange(cint(msd.year) ,cint(month))[1]) # days in month
        med = datetime.date(msd.year, cint(month), month_days) # month end date
    return_list = []
    default_count_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0]

    ses_details = frappe.db.sql("""SELECT branch,parent_sales_person,name,contact_number,designation FROM `tabSales Person` WHERE show_in_daily_report = 1 ORDER BY branch ASC""",as_list = True )
    lead_details = frappe.db.sql("""SELECT date,sales_person FROM `tabLead` WHERE date >= %s AND date <= %s """,(msd,med),as_list = True )

    my_local_list = []
    for se in ses_details:
        my_local_list.append(se[2])
    count =  {key: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0] for key in my_local_list}

    for lead in lead_details:
        if lead[1] in count:
            my_day = lead[0].day
            count[lead[1]][my_day - 1] +=1

    for se in ses_details:
        count[se[2]].append(sum(count[se[2]]))
        se_list = se + count[se[2]]
        return_list.append(se_list)

    my_list_of_list = []
    my_total_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0]
    for key in count:
        my_list_of_list.append(count[key])
    my_total_list = map(sum, zip(*my_list_of_list))
    my_total_list = ["<b>Daily Total</b>","","","",""] + my_total_list

    return_list.append(my_total_list)
    return return_list


def get_columns():
    return [
        _("Branch") + ":Link/Branch:100",
        _("Senior Manger") + ":Link/Sales Person:100",
        _("Name of SE") + ":Link/Sales Person:100",
        _("SE Contact Number") + ":Data:130",
        _("Designation") + ":Data:130",
        _("1st") + ":Int:40",
        _("2nd") + ":Int:40",
        _("3rd") + ":Int:40",
        _("4th") + ":Int:40",
        _("5th") + ":Int:40",
        _("6th") + ":Int:40",
        _("7th") + ":Int:40",
        _("8th") + ":Int:40",
        _("9st") + ":Int:40",
        _("10th") + ":Int:40",
        _("11th") + ":Int:40",
        _("12th") + ":Int:40",
        _("13th") + ":Int:40",
        _("14th") + ":Int:40",
        _("15th") + ":Int:40",
        _("16th") + ":Int:40",
        _("17th") + ":Int:40",
        _("18th") + ":Int:40",
        _("19th") + ":Int:40",
        _("20th") + ":Int:40",
        _("21st") + ":Int:40",
        _("22nd") + ":Int:40",
        _("23rd") + ":Int:40",
        _("24th") + ":Int:40",
        _("25th") + ":Int:40",
        _("26th") + ":Int:40",
        _("27th") + ":Int:40",
        _("28th") + ":Int:40",
        _("29th") + ":Int:40",
        _("30th") + ":Int:40",
        _("31st") + ":Int:40",
        _("Total") + ":Int:40"
        ]
