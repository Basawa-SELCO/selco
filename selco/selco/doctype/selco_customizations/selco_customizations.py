# -*- coding: utf-8 -*-
# Copyright (c) 2015, Selco and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SelcoCustomizations(Document):
    pass

@frappe.whitelist()
def selco_issue_updates(doc,method):
    if doc.workflow_state =="Complaint Open":
        if not doc.customer_address:
            frappe.throw("Please Enter Customer Address")
    if doc.workflow_state =="Complaint Closed By Branch":
        if not doc.service_record_details:
            frappe.throw(("Please Enter Service Record Details Before Closing the Complaint"))
        cur_date = now_datetime().date()
        doc.complaint_closed_date = cur_date
        doc.status = "Closed"
        doc.resolution_date = now()


@frappe.whitelist()
def selco_warranty_claim_updates(doc,method):
    if doc.workflow_state =="Dispatched From Godown":
        doc.status = "Closed"

@frappe.whitelist()
def selco_delivery_note_updates(doc,method):
    selco_warehouse  = frappe.db.get_value("Branch",doc.branch,"selco_warehouse")
    selco_cost_center = frappe.db.get_value("Warehouse",selco_warehouse,"cost_center")
    for d in doc.get('items'):
        d.warehouse = selco_warehouse
        d.cost_center = selco_cost_center

@frappe.whitelist()
def selco_material_request_updates(doc,method):
	#Start of Insert By Poorvi on 10-09-2016 for IBM value calculation
	selco_ibm_value = 0
	#if doc.workflow_state =="Approval Pending by SM - IBM":
	for idx,selco_item in enumerate(doc.items):
		selco_rate = frappe.db.sql("""select price_list_rate
			from `tabItem Price`
			where item_code = %s and price_list = "Branch Sales" """,(selco_item.item_code))
		if selco_rate:
			var1=selco_rate[0][0]
		else:
			var1=0
		doc.items[idx].selco_rate =var1
		selco_ibm_value = selco_ibm_value + (var1 * selco_item.qty)
	doc.selco_ibm_value = selco_ibm_value
	#doc.items.sort(key = lambda x: x.item_code)
	doc.items.sort(key=operator.attrgetter("item_code"), reverse=False)
	#Start of Insert By Poorvi on 08-02-2017
	from frappe.utils import now,now_datetime
	if doc.workflow_state == "Approved - IBM":
		 doc.approved_time = now()
	if doc.workflow_state == "Dispatched From Godown - IBM":
		 doc.dispatched_time = now()
	#End of Insert By Poorvi on 08-02-2017

@frappe.whitelist()
def selco_purchase_receipt_updates(doc,method):
	selco_cost_center = frappe.db.get_value("Warehouse",doc.godown,"cost_center")
	for d in doc.get('items'):
		d.cost_center = selco_cost_center
	for d in doc.get('taxes'):
		d.cost_center = selco_cost_center
	po_list = []
	po_list_date = []
	for item_selco in doc.items:
		if item_selco.prevdoc_docname not in po_list:
			po_list.append(item_selco.prevdoc_docname)
			po_list_date.append(frappe.utils.formatdate(frappe.db.get_value('Purchase Order', item_selco.prevdoc_docname, 'transaction_date'),"dd-MM-yyyy"))
	doc.selco_list_of_po= ','.join([str(i) for i in po_list])
	doc.selco_list_of_po_date= ','.join([str(i) for i in po_list_date])
	#End of Insert By basawaraj On 7th september for printing the list of PO when PR is done by importing items from multiple PO

@frappe.whitelist()
def selco_stock_entry_updates(doc,method):
    #Inserted By basawaraj On 21st Dec
    if doc.purpose=="Material Transfer":
        selco_cost_center = frappe.db.get_value("Warehouse",doc.to_warehouse,"cost_center")
        for d in doc.get('items'):
            d.cost_center = selco_cost_center
    if doc.purpose == "Material Issue":
        selco_cost_center = frappe.db.get_value("Warehouse",doc.from_warehouse,"cost_center")
        for d in doc.get('items'):
            d.expense_account = "Stock Adjustment - SELCO"
            d.cost_center = selco_cost_center
    #End of Insert By basawaraj On 21st Dec
