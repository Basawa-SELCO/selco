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

def execute(filters=None):
    columns, data = [], []
    columns = get_columns1()
    data1 = get_data(filters)
    for d in data1:
        row = []
        row = [d.name,d.branch,d.posting_date,d.party_name,d.received_amount,d.financing_institution,d.financing_institution_branch]
        data.append(row)
    return columns, data

def get_columns1():
    return [
    _("Receipt Number") + ":Link/Payment Entry:140",_("Branch") + ":Link/Branch",_("Date") + ":Date:80",_("Party Name") + ":Data:180",_("Received Amount") + ":Currency:100",_("Financing Institution") + ":Link/Financing Institution:140",_("Financing Institution Branch") + ":Link/Financing Institution Branch:140"]

def get_data(filters):
    conditions = ""
    values = []
    msd = "0000/00/00"
    med = "0000/00/00"
    fiscal_year = filters.get("fiscal_year")
    if filters.get("fiscal_year"):
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
            "Dec","All Months"].index(filters["month_number"]) + 1
        ysd = frappe.db.get_value("Fiscal Year", fiscal_year, "year_start_date")
        #frappe.msgprint(ysd)
    from dateutil.relativedelta import relativedelta
    import calendar, datetime
    if month <= 12:
        diff_mnt = cint(month)-cint(ysd.month)
        if diff_mnt<0:
            diff_mnt = 12-int(ysd.month)+cint(month)
        msd = ysd + relativedelta(months=diff_mnt) # month start date
        month_days = cint(calendar.monthrange(cint(msd.year) ,cint(month))[1]) # days in month
        med = datetime.date(msd.year, cint(month), month_days) # month end date
    else:
        msd = frappe.db.get_value("Fiscal Year", fiscal_year, "year_start_date")
        med = frappe.db.get_value("Fiscal Year", fiscal_year, "year_end_date")

    return frappe.db.sql("""SELECT name,branch,posting_date,party_name,received_amount,financing_institution,financing_institution_branch FROM `tabPayment Entry`  WHERE financed  = 'YES'
and financing_institution != 'SKDRDP' and posting_date BETWEEN %s AND %s ORDER BY financing_institution,financing_institution_branch,posting_date""",(msd,med),as_dict=1)
