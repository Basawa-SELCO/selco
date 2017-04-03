"""# Copyright (c) 2013, Selco and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [], []
	return columns, data"""

# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
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
	columns = get_columns()
	data = get_lead_details(filters)
	"""for lead in leads:
		row = [lead.branch,"Yallaling G Doddamani",lead.sales_person,"9900038803","Sales Executive"]
		data.append(row)"""
	return columns, data


def get_columns():
	return [
		_("Branch") + ":Link/Branch:100", _("Senior Manger") + ":Data:110",_("Name of SE") + ":Data:120",_("SE Contact Number") + ":Data:130",_("Designation") + ":Data:130",_("1st") + ":Int:40",_("2nd") + ":Int:40",_("3rd") + ":Int:40", _("4th") + ":Int:40",_("5th") + ":Int:40",_("6th") + ":Int:40",_("7th") + ":Int:40",_("8th") + ":Int:40"
		]
def get_lead_details(filters):

	conditions = ""
	values = []
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

	branches,branches_with_name = [], []
	branches_with_ses = []
	count1,count2,count3,count4,count5,count6,count7,count8 = 0,0,0,0,0,0,0,0

	branches = frappe.db.sql("""SELECT name,senior_manager FROM `tabBranch` """,as_dict=1)
	for branch in branches:
		ses = frappe.db.sql("""SELECT sales_person_name,contact_number,designation FROM `tabSales Person` WHERE parent_sales_person = %s""",(branch.senior_manager),as_dict=1)
		cur_date = msd
		for se in ses:
			count1 = frappe.db.sql("""SELECT COUNT(name) FROM `tabLead` WHERE sales_person = %s AND date = %s""",(se.sales_person_name,cur_date))
			cur_date += datetime.timedelta(days=1)
			count2 = frappe.db.sql("""SELECT COUNT(name) FROM `tabLead` WHERE sales_person = %s AND date = %s""",(se.sales_person_name,cur_date))
			cur_date += datetime.timedelta(days=1)
			count3 = frappe.db.sql("""SELECT COUNT(name) FROM `tabLead` WHERE sales_person = %s AND date = %s""",(se.sales_person_name,cur_date))
			cur_date += datetime.timedelta(days=1)
			count4 = frappe.db.sql("""SELECT COUNT(name) FROM `tabLead` WHERE sales_person = %s AND date = %s""",(se.sales_person_name,cur_date))
			cur_date += datetime.timedelta(days=1)
			count5 = frappe.db.sql("""SELECT COUNT(name) FROM `tabLead` WHERE sales_person = %s AND date = %s""",(se.sales_person_name,cur_date))
			cur_date += datetime.timedelta(days=1)
			count6 = frappe.db.sql("""SELECT COUNT(name) FROM `tabLead` WHERE sales_person = %s AND date = %s""",(se.sales_person_name,cur_date))
			cur_date += datetime.timedelta(days=1)
			count7 = frappe.db.sql("""SELECT COUNT(name) FROM `tabLead` WHERE sales_person = %s AND date = %s""",(se.sales_person_name,cur_date))
			cur_date += datetime.timedelta(days=1)
			count8 = frappe.db.sql("""SELECT COUNT(name) FROM `tabLead` WHERE sales_person = %s AND date = %s""",(se.sales_person_name,cur_date))

			var1 = [branch.name,branch.senior_manager,se.sales_person_name,se.contact_number,se.designation,count1[0][0],count2[0][0],count3[0][0],count4[0][0],count5[0][0],count6[0][0],count7[0][0],count8[0][0]]
			branches_with_ses.append(var1)
		cur_date = msd
	return branches_with_ses
