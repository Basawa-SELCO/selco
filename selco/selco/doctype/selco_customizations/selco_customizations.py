# -*- coding: utf-8 -*-
# Copyright (c) 2015, Selco and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import now,now_datetime
import operator



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
        if not d.rate:
            d.rate = frappe.db.get_value("Item Price",{"price_list": "Branch Sales","item_code":d.item_code}, "price_list_rate")

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
        if item_selco.purchase_order not in po_list:
            po_list.append(item_selco.purchase_order)
            po_list_date.append(frappe.utils.formatdate(frappe.db.get_value('Purchase Order', item_selco.purchase_order, 'transaction_date'),"dd-MM-yyyy"))
    doc.selco_list_of_po= ','.join([str(i) for i in po_list])
    doc.selco_list_of_po_date= ','.join([str(i) for i in po_list_date])
    #End of Insert By basawaraj On 7th september for printing the list of PO when PR is done by importing items from multiple PO

@frappe.whitelist()
def selco_stock_entry_updates(doc,method):
    #Inserted By basawaraj On 21st Dec
    if doc.purpose=="Repack":
        doc.naming_series = frappe.db.get_value("Branch",doc.branch,"bill_of_material_naming_series")
    if doc.purpose=="Material Transfer":
        selco_cost_center = frappe.db.get_value("Warehouse",doc.to_warehouse,"cost_center")
        for d in doc.get('items'):
            d.cost_center = selco_cost_center
    if doc.purpose == "Material Issue":
        selco_cost_center = frappe.db.get_value("Warehouse",doc.from_warehouse,"cost_center")
        for d in doc.get('items'):
            d.expense_account = "Stock Adjustment - SELCO"
            d.cost_center = selco_cost_center
    if doc.purpose=="Repack":
        if doc.from_warehouse != doc.to_warehouse:
            frappe.throw("While repacking From and To Warehouses must be same");
        selco_cost_center = frappe.db.get_value("Warehouse",doc.to_warehouse,"cost_center")
        for d in doc.get('items'):
            d.cost_center = selco_cost_center
    #End of Insert By basawaraj On 21st Dec

@frappe.whitelist()
def selco_customer_before_insert(doc,method):
    doc.naming_series = frappe.db.get_value("Branch",doc.branch,"customer_naming_series")

@frappe.whitelist()
def selco_customer_updates(doc,method):
    doc.naming_series = frappe.db.get_value("Branch",doc.branch,"customer_naming_series")
    if not ( doc.customer_contact_number or doc.landline_mobile_2 ):
        frappe.throw("Enter either Customer Contact Number ( Mobile 1 ) or Landline / Mobile 2")
    var4 = frappe.db.get_value("Customer", {"customer_contact_number": (doc.customer_contact_number)})
    var5 = unicode(var4) or u''
    var6 = frappe.db.get_value("Customer", {"customer_contact_number": (doc.customer_contact_number)}, "customer_name")
    if var5 != "None" and doc.name != var5:
        frappe.throw("Customer with contact no " + doc.customer_contact_number + " already exists \n Customer ID : " + var5 + "\n Customer Name : " + var6)
    var14 = frappe.db.get_value("Customer", {"landline_mobile_2": (doc.landline_mobile_2)})
    var15 = unicode(var14) or u''
    var16 = frappe.db.get_value("Customer", {"landline_mobile_2": (doc.landline_mobile_2)}, "customer_name")
    if var15 != "None" and doc.name != var15:
        frappe.throw("Customer with Landline Number " + doc.landline_mobile_2 + " already exists \n Customer ID : " + var15 + "\n Customer Name : " + var16)

@frappe.whitelist()
def get_items_from_outward_stock_entry(selco_doc_num,selco_branch):
    selco_var_dc = frappe.get_doc("Stock Entry",selco_doc_num)
    from_warehouse = frappe.db.get_value("Branch",selco_branch,"git_warehouse")
    to_warehouse = frappe.db.get_value("Branch",selco_branch,"selco_warehouse")
    return { 'dc' : selco_var_dc,'from_warehouse' : from_warehouse, 'to_warehouse' :to_warehouse }

@frappe.whitelist()
def selco_sales_invoice_before_insert(doc,method):
    if doc.is_return == 1:
        doc.naming_series = frappe.db.get_value("Branch",doc.branch,"credit_note_naming_series")
    else:
        if doc.type_of_invoice == "System Sales Invoice" or doc.type_of_invoice == "Spare Sales Invoice":
            doc.naming_series = frappe.db.get_value("Branch",doc.branch,"sales_invoice_naming_series")
        elif doc.type_of_invoice == "Service Bill":
            doc.naming_series = frappe.db.get_value("Branch",doc.branch,"service_bill_naming_series")
        elif doc.type_of_invoice == "Bill of Sale":
            doc.naming_series = frappe.db.get_value("Branch",doc.branch,"bill_of_sales_naming_series")

    selco_warehouse  = frappe.db.get_value("Branch",doc.branch,"selco_warehouse")
    selco_cost_center = frappe.db.get_value("Warehouse",selco_warehouse,"cost_center")
    for d in doc.get('items'):
        d.cost_center = selco_cost_center
        d.income_account = doc.sales_account
    for d in doc.get('taxes'):
        d.cost_center = selco_cost_center

def selco_payment_entry_before_insert(doc,method):
    if doc.payment_type == "Receive":
        doc.naming_series = frappe.db.get_value("Branch",doc.branch,"receipt_naming_series")
        #if doc.mode_of_payment == "Bank":
        doc.paid_to = frappe.db.get_value("Branch",doc.branch,"collection_account")
    elif doc.payment_type == "Pay":
        if doc.mode_of_payment == "Bank":
            doc.naming_series = frappe.db.get_value("Branch",doc.branch,"bank_payment_naming_series")

def selco_journal_entry_before_insert(doc,method):
    local_cost_center = frappe.db.get_value("Branch",doc.branch,"cost_center")
    for account in doc.accounts:
        account.cost_center = local_cost_center
    if doc.voucher_type == "Contra Entry":
        doc.naming_series = frappe.db.get_value("Branch",doc.branch,"contra_naming_series")
        if doc.branch == "Head Office" and doc.transfer_type == "Branch Collectiion To Platinum":
            doc.naming_series = frappe.db.get_value("Branch",doc.branch,"bank_payment_collection")
        elif doc.branch == "Head Office" and doc.transfer_type == "Platinum To Branch Expenditure":
            doc.naming_series = frappe.db.get_value("Branch",doc.branch,"bank_payment_expenditure")
    if doc.voucher_type == "Cash Payment":
        doc.naming_series = frappe.db.get_value("Branch",doc.branch,"cash_payment_naming_series")
    if doc.voucher_type == "Debit Note":
        doc.naming_series = frappe.db.get_value("Branch",doc.branch,"debit_note_naming_series")
    if doc.voucher_type == "Credit Note":
        doc.naming_series = frappe.db.get_value("Branch",doc.branch,"credit_note_naming_series")
    if doc.voucher_type == "Journal Entry":
        doc.naming_series = frappe.db.get_value("Branch",doc.branch,"journal_entry_naming_series")
    if doc.voucher_type == "Write Off Entry":
        doc.naming_series = frappe.db.get_value("Branch",doc.branch,"write_off_naming_series")

@frappe.whitelist()
def selco_purchase_invoice_before_insert(doc,method):
    if doc.is_return == 1:
        doc.naming_series = "DN/HO/16-17/"

@frappe.whitelist()
def clean_up(doc,method):
    #var1 = frappe.get_doc("Purchase Receipt", "MRN/S/17/004")
    #var1.cancel()
    #frappe.delete_doc("Purchase Receipt", var1.name)
    #frappe.msgprint("Triggered")
