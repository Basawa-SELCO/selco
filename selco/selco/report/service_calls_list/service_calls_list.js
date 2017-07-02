// For license information, please see license.txt
// Copyright (c) 2016, Selco and contributors

frappe.query_reports["Service Calls List"] = {
	"filters": [
		{
			"fieldname":"month",
			"label":__("Month"),
			"fieldtype":"Select",
			"options":"January\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
			"default":["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
			"December"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()]
		}
	]
}
