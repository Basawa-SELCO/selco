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

def execute(filters):
	columns, data, initial = [], [],[]
	columns= get_columns()
	initial = get_data(filters)	#unorganized data

	ins_sb=[]						#insentive service branch
	ins_ist=[]						#insentive installation
	no_sb=[]						#no insentive service branch
	no_ist=[]						#no insentive installation
	total_ins=[]					#total eligibe CSE for insentive
	total_no=[]						#total uneligible CSE for insentive

	for d in initial:
		if d[5]=="Service" :
			if int(d[6])>99 :
				ins_sb.append(d)
			else :
				no_sb.append(d)
		else:
			if int(d[6]>53) :
				ins_ist.append(d)
			else :
				no_ist.append(d)

	if(len(initial)>0):
		total_ins=[""]*len(initial[0])
		total_no=[""]*len(initial[0])
		info_sb=[""]*len(initial[0])											#string info service with insentive
		info_no_sb=[""]*len(initial[0])											#string info service without insentive
		info_ins=[""]*len(initial[0])											#string info Installation with insentive
		info_no_ins=[""]*len(initial[0])										#string info Installation without insentive
	else:
		return columns, data


	tot_ins = len(ins_sb)+len(ins_ist)											#Total eligible CSE
	tot_no = len(no_sb)+len(no_ist)												#Total uneligible CSE
	total_ins[2]='<b>&nbsp;&emsp;&emsp;<u>TOTAL</u>-</b>'
	total_ins[3]='<b><u>ELIGIBLE CSE</u> : </b>'+'<b>'+str(tot_ins)+'</b>'
	total_no[2]='<b>&emsp;&emsp;&nbsp;<u>TOTAL</u>-</b>'
	total_no[3]='<b><u>UNELIGIBLE CSE</u> : </b>'+'<b>'+str(tot_no)+'</b>'
	#total_ins[4]='<b>'+str(tot_ins)+'</b>'
	#total_no[4]='<b>'+str(tot_no)+'</b>'

	data.append(total_ins)
	data.append(total_no)

	if(len(ins_sb)>0):

		info_sb[0]='<center><u><b>Eligible CSE (Service) : </u></center></b>'#+ str((len(ins_sb)))+'</b>'
		info_sb[1]='<b>'+str((len(ins_sb)))+'</b>'
		data.append(info_sb)
		data=data+ins_sb

	if(len(no_sb)>0):

		info_no_sb[0]='<center><u><b>Ineligible CSE (Service) : </u></center></b>' #+ str(len(no_sb))+'</b>'
		info_no_sb[1]='<b>'+ str(len(no_sb))+'</b>'
		data.append(info_no_sb)
		data=data+no_sb

	if(len(ins_ist)>0):

		info_ins[0]='<center><u><b>Eligible CSE(Installation):</u></center></b>'#+str(len(ins_ist))+'</b>'
		info_ins[1]='<b>'+str(len(ins_ist))+'</b>'
		data.append(info_ins)
		data=data+ins_ist

	if(len(no_ist)>0):

		info_no_ins[0]='<center><u><b>Inligible CSE(Installation):</u></center></b>'#+ str(len(no_ist))+'</b>'
		info_no_ins[1]='<b>'+ str(len(no_ist))+'</b>'
		data.append(info_no_ins)
		data=data+no_ist

	total=get_sum(initial)			#sum of calls for each day
	data.append(total)



	return columns, data

def get_columns():
	return[
		("Branch")+":Link/Branch:165",
		("Sr. MGR Name")+":Link/Service Person:135",
		("P/T")+":Data:80",
		("Name of CSE")+":Link/Service Person:140",
		("CSE Contact No")+":Data:100",
		("Service/Installation")+":Data:85",
		("Row Total")+":Data:75",
		("Day 1")+":Data:50",("Day 2")+":Data:50",("Day 3")+":Data:50",("Day 4")+":Data:50",
		("Day 5")+":Data:50",("Day 6")+":Data:50",("Day 7")+":Data:50",("Day 8")+":Data:50",
		("Day 9")+":Data:50",("Day 10")+":Data:50",("Day 11")+":Data:50",("Day 12")+":Data:50",
		("Day 13")+":Data:50",("Day 14")+":Data:50",("Day 15")+":Data:50",("Day 16")+":Data:50",
		("Day 17")+":Data:50",("Day 18")+":Data:50",("Day 19")+":Data:50",("Day 20")+":Data:50",
		("Day 21")+":Data:50",("Day 22")+":Data:50",("Day 23")+":Data:50",("Day 24")+":Data:50",
		("Day 25")+":Data:50",("Day 26")+":Data:50",("Day 27")+":Data:50",("Day 28")+":Data:50",
		("Day 29")+":Data:50",("Day 30")+":Data:50",("Day 31")+":Data:50"

	]

def get_data(filters):
	mnth=filters.get("month")
	return frappe.db.sql("""
	SELECT A.branch,C.reports_to,C.status,B.service_person,C.contact_number,C.service_or_installation,
	B.day1+B.day2+B.day3+B.day4+B.day5+B.day6+B.day7+B.day8+B.day9+B.day10+B.day11+B.day12+B.day13+B.day14+B.day15+B.day16+
	B.day17+B.day18+B.day19+B.day20+B.day21+B.day22+B.day23+B.day24+B.day25+B.day26+B.day27+B.day28+B.day29+B.day30+B.day31,
	B.day1,B.day2,B.day3,B.day4,B.day5,B.day6,B.day7,B.day8,B.day9,B.day10,B.day11,B.day12,B.day13,B.day14,B.day15,B.day16,
	B.day17,B.day18,B.day19,B.day20,B.day21,B.day22,B.day23,B.day24,B.day25,B.day26,B.day27,B.day28,B.day29,B.day30,B.day31
	FROM `tabService Call` AS A INNER JOIN
	`tabService Call Details` AS B INNER JOIN
	`tabService Person` AS C ON A.name=B.parent
	AND B.service_person=C.service_person_name
	WHERE A.month= %s
	ORDER BY B.day1+B.day2+B.day3+B.day4+B.day5+B.day6+B.day7+B.day8+B.day9+B.day10+
	B.day11+B.day12+B.day13+B.day14+B.day15+B.day16+B.day17+B.day18+B.day19+B.day20+B.day21+B.day22+B.day23+B.day24+B.day25+
	B.day26+B.day27+B.day28+B.day29+B.day30+B.day31 DESC""",(mnth),as_list=1)
	#B.day1+B.day2+B.day3+B.day4+B.day5+B.day6+B.day7+B.day8+B.day9+B.day10+B.day11+B.day12+B.day13+B.day14+B.day15+B.day16+B.day17+B.day18+B.day19+B.day20+B.day21+B.day22+B.day23+B.day24+B.day25+B.day26+B.day27+B.day28+B.day29+B.day30+B.day31

#sum of calls for each day
def get_sum(data):
	total=[0]*len(data[0])

	for i in range(0,len(data)) :
		for j in range(7,len(data[i])) :
			total[j]=total[j]+data[i][j]

	total[6]="<b>Col Total</b>"
	for i in range(0,6):
		total[i]=""
	return total


"""
install 54
service brnch 100
temp after 1mnth
"""
