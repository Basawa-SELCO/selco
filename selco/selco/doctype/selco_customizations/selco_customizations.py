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
    var4 = frappe.db.get_value("Warranty Claim", {"complaint_number": (doc.complaint_number)})
    var5 = unicode(var4) or u''
    var6 = frappe.db.get_value("Warranty Claim", {"complaint_number": (doc.complaint_number)}, "customer_full_name")
    if var5 != "None" and doc.name != var5:
        frappe.throw("Warranty Claim for complaint " + doc.complaint_number + " already exists. <br /> Warranty Claim Number : " + var5 + "<br /> Customer Name : " + var6 + "<br /> You cannot link same complaint for tow warranty claims.<br />Please create another complaint.")
    if doc.workflow_state =="Dispatched From Godown":
        doc.status = "Closed"
    if doc.complaint_number:
        complaint = frappe.get_doc("Issue",doc.complaint_number)
        complaint.warranty_claim_number = doc.name
        complaint.save()


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
def selco_delivery_note_before_insert(doc,method):
    if doc.is_return:
        doc.naming_series = "DC-RET/"
    else:
        doc.naming_series = frappe.db.get_value("Branch",doc.branch,"delivery_note_naming_series")
    selco_warehouse  = frappe.db.get_value("Branch",doc.branch,"selco_warehouse")
    selco_cost_center = frappe.db.get_value("Warehouse",selco_warehouse,"cost_center")
    for d in doc.get('items'):
        d.warehouse = selco_warehouse
        d.cost_center = selco_cost_center
        if not d.rate:
            d.rate = frappe.db.get_value("Item Price",{"price_list": "Branch Sales","item_code":d.item_code}, "price_list_rate")

@frappe.whitelist()
def selco_material_request_before_insert(doc,method):
    doc.naming_series = frappe.db.get_value("Branch",doc.branch,"material_request_naming_series")
    local_warehouse = frappe.db.get_value("Branch",doc.branch,"git_warehouse")
    for d in doc.get('items'):
        if not d.warehouse:
            d.warehouse = local_warehouse

@frappe.whitelist()
def selco_material_request_updates(doc,method):
    doc.items.sort(key=operator.attrgetter("item_code"), reverse=False)
    if doc.workflow_state == "Approved - IBM":
         doc.approved_time = now()
    if doc.workflow_state == "Partially Dispatched From Godown - IBM":
        flag = "N"
        for d in doc.get('items'):
            if d.dispatched_quantity != 0:
                flag = "Y"
        for d in doc.get('items'):
            if flag != "Y":
                d.dispatched_quantity = d.qty
    if doc.workflow_state == "Dispatched From Godown - IBM":
        doc.dispatched_time = now()
        for d in doc.get('items'):
            d.dispatched_quantity = d.qty
    #End of Insert By Poorvi on 08-02-2017

@frappe.whitelist()
def selco_purchase_receipt_before_insert(doc,method):
    doc.naming_series = frappe.db.get_value("Warehouse",doc.godown,"mrn_naming_series")

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
def test_before_save(doc,method):
    pass #frappe.msgprint("Before Save")

@frappe.whitelist()
def selco_stock_entry_updates(doc,method):
    selco_cost_center = frappe.db.get_value("Branch",doc.branch,"cost_center")
    selco_selco_warehouse = frappe.db.get_value("Branch",doc.branch,"selco_warehouse")
    selco_repair_warehouse = frappe.db.get_value("Branch",doc.branch,"repair_warehouse")

    if doc.purpose=="Material Transfer":
        if doc.inward_or_outward=="Inward":
            doc.naming_series = frappe.db.get_value("Branch",doc.branch,"receipt_note_naming_series")
            if doc.type_of_material=="Good Stock":
                for d in doc.get('items'):
                    d.cost_center = selco_cost_center
                    d.from_warehouse = "SELCO GIT - SELCO"
                    d.to_warehouse = selco_selco_warehouse
            else:
                for d in doc.get('items'):
                    d.s_warehouse = "SELCO GIT Repair - SELCO"
                    d.t_warehouse = selco_repair_warehouse
                    d.cost_center = selco_cost_center
                    d.is_sample_item = 1
        elif doc.inward_or_outward=="Outward":
            doc.naming_series = frappe.db.get_value("Branch",doc.branch,"delivery_note_naming_series")
            if doc.type_of_material=="Good Stock":
                doc.from_warehouse = selco_selco_warehouse
                doc.to_warehouse = "SELCO GIT - SELCO"
                for d in doc.get('items'):
                    d.s_warehouse = selco_selco_warehouse
                    d.t_warehouse = "SELCO GIT - SELCO"
                    d.cost_center = selco_cost_center
            else:
                doc.from_warehouse = selco_repair_warehouse
                doc.to_warehouse = "SELCO GIT Repair - SELCO"
                for d in doc.get('items'):
                    d.s_warehouse = selco_repair_warehouse
                    d.t_warehouse = "SELCO GIT Repair - SELCO"
                    d.cost_center = selco_cost_center
                    d.is_sample_item = 1
    elif doc.purpose=="Material Receipt":
        doc.naming_series = frappe.db.get_value("Branch",doc.branch,"rejection_in_naming_series")
        doc.to_warehouse = selco_repair_warehouse
        for d in doc.get('items'):
            d.t_warehouse = selco_repair_warehouse
            d.cost_center = selco_cost_center
            d.is_sample_item = 1
    elif doc.purpose=="Material Issue":
        doc.naming_series = frappe.db.get_value("Branch",doc.branch,"rejection_out__naming_series")
        doc.from_warehouse = selco_repair_warehouse
        for d in doc.get('items'):
            d.f_warehouse = selco_repair_warehouse
            d.cost_center = selco_cost_center
            d.is_sample_item = 1
    elif doc.purpose=="Repack":
        doc.naming_series = frappe.db.get_value("Branch",doc.branch,"bill_of_material_naming_series")
        for d in doc.get('items'):
            d.cost_center = selco_cost_center
            d.s_warehouse = selco_selco_warehouse
            d.t_warehouse = selco_selco_warehouse

@frappe.whitelist()
def get_items_from_outward_stock_entry(selco_doc_num,selco_branch):
    selco_var_dc = frappe.get_doc("Stock Entry",selco_doc_num)
    if selco_var_dc.being_dispatched_to != selco_branch:
        frappe.throw("Incorrect DC Number");
    from_warehouse = selco_var_dc.to_warehouse
    if selco_var_dc.type_of_material=="Good Stock":
        to_warehouse = frappe.db.get_value("Branch",selco_var_dc.being_dispatched_to,"selco_warehouse")
    else:
        to_warehouse = frappe.db.get_value("Branch",selco_var_dc.being_dispatched_to,"repair_warehouse")
    return { 'dc' : selco_var_dc,'from_warehouse' : from_warehouse, 'to_warehouse' :to_warehouse }

@frappe.whitelist()
def get_items_from_rejection_in(selco_rej_in,selco_branch):
    selco_var_dc = frappe.get_doc("Stock Entry",selco_rej_in)
    return { 'dc' : selco_var_dc }

    """frappe.msgprint("Button Clicked");
    selco_cost_center = frappe.db.get_value("Branch",selco_branch,"cost_center")
    selco_selco_warehouse = frappe.db.get_value("Branch",selco_branch,"selco_warehouse")
    selco_repair_warehouse = frappe.db.get_value("Branch",selco_branch,"repair_warehouse")

    outward_dc = frappe.get_doc("Stock Entry",selco_doc_num)
    if outward_dc.type_of_material=="Good Stock":
        for d in outward_dc.get('items'):
            d.s_warehouse = "SELCO GIT - SELCO"
            d.t_warehouse = selco_selco_warehouse
            d.cost_center = selco_cost_center
    else:
        for d in outward_dc.get('items'):
            d.s_warehouse = "SELCO GIT Repair - SELCO"
            d.t_warehouse = selco_selco_warehouse
            d.cost_center = selco_cost_center"""

@frappe.whitelist()
def selco_customer_before_insert(doc,method):
    doc.naming_series = frappe.db.get_value("Branch",doc.branch,"customer_naming_series")

@frappe.whitelist()
def selco_customer_updates(doc,method):
    doc.naming_series = frappe.db.get_value("Branch",doc.branch,"customer_naming_series")
    if not ( doc.customer_contact_number or doc.landline_mobile_2 ):
        frappe.throw("Enter either Customer Contact Number ( Mobile 1 ) or Mobile 2 / Landline")
    if doc.customer_contact_number:
        if len(doc.customer_contact_number) != 10:
            frappe.throw("Invalid Customer Contact Number ( Mobile 1 ) - Please enter exact 10 digits of mobile no ex : 9900038803")
        selco_validate_if_customer_contact_number_exists(doc.customer_contact_number,doc.name)
    if doc.landline_mobile_2:
        selco_validate_if_customer_contact_number_exists(doc.landline_mobile_2,doc.name)

def selco_validate_if_customer_contact_number_exists(contact_number,customer_id):
    var4 = frappe.db.get_value("Customer", {"customer_contact_number": (contact_number)})
    var5 = unicode(var4) or u''
    var6 = frappe.db.get_value("Customer", {"customer_contact_number": (contact_number)}, "customer_name")
    if var5 != "None" and customer_id != var5:
        frappe.throw("Customer with contact no " + contact_number + " already exists \n Customer ID : " + var5 + "\n Lead Name : " + var6)

    var14 = frappe.db.get_value("Customer", {"landline_mobile_2": (contact_number)})
    var15 = unicode(var14) or u''
    var16 = frappe.db.get_value("Customer", {"landline_mobile_2": (contact_number)}, "customer_name")
    if var15 != "None" and customer_id != var15:
        frappe.throw("Customer with contact no " + contact_number + " already exists \n Customer ID : " + var15 + "\n Lead Name : " + var16)


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

@frappe.whitelist()
def selco_sales_invoice_on_submit(doc,method):
    #selco_warehouse  = frappe.db.get_value("Branch",doc.branch,"selco_warehouse")
    selco_cost_center = frappe.db.get_value("Branch",doc.branch,"cost_center")
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
    if doc.voucher_type == "Bank Payment":
        doc.naming_series = frappe.db.get_value("Branch",doc.branch,"bank_payment_naming_series")

@frappe.whitelist()
def selco_purchase_invoice_before_insert(doc,method):
    if doc.is_return == 1:
        doc.naming_series = "DN/HO/16-17/"

@frappe.whitelist()
def selco_purchase_invoice_validate(doc,method):
    doc.posting_date = doc.supplier_invoice_date
    doc.due_date = doc.supplier_invoice_date
    doc.bill_no = doc.supplier_invoice_number

@frappe.whitelist()
def clean_up(doc,method):
    var1 = 1
    #var1 = frappe.get_doc("Purchase Receipt", "MRN/S/17/004")
    #var1.cancel()
    #frappe.delete_doc("Purchase Receipt", var1.name)
    #frappe.msgprint("Triggered")

@frappe.whitelist()
def selco_lead_before_insert(doc,method):
    doc.naming_series = frappe.db.get_value("Branch",doc.branch,"lead_naming_series")
    if doc.project_enquiry == 1:
        doc.naming_series = "ENQ/17-18/"

@frappe.whitelist()
def selco_lead_validate(doc,method):
    if not ( doc.customer_contact_number or doc.customer_contact_number_landline ):
        frappe.throw("Enter either Customer Contact Number ( Mobile 1 ) or Mobile 2 / Landline")
    if doc.customer_contact_number:
        if len(doc.customer_contact_number) != 10:
            frappe.throw("Invalid Customer Contact Number ( Mobile 1 ) - Please enter exact 10 digits of mobile no ex : 9900038803")
        selco_validate_if_lead_contact_number_exists(doc.customer_contact_number,doc.name)
    if doc.customer_contact_number_landline:
        selco_validate_if_lead_contact_number_exists(doc.customer_contact_number_landline,doc.name)


def selco_validate_if_lead_contact_number_exists(contact_number,lead_id):
    var4 = frappe.db.get_value("Lead", {"customer_contact_number_landline": (contact_number)})
    var5 = unicode(var4) or u''
    var6 = frappe.db.get_value("Lead", {"customer_contact_number_landline": (contact_number)}, "lead_name")
    if var5 != "None" and lead_id != var5:
        frappe.throw("Lead with contact no " + contact_number + " already exists \n Lead ID : " + var5 + "\n Lead Name : " + var6)

    var14 = frappe.db.get_value("Lead", {"customer_contact_number": (contact_number)})
    var15 = unicode(var14) or u''
    var16 = frappe.db.get_value("Lead", {"customer_contact_number": (contact_number)}, "lead_name")
    if var15 != "None" and lead_id != var15:
        frappe.throw("Lead with contact no " + contact_number + " already exists \n Lead ID : " + var15 + "\n Lead Name : " + var16)

@frappe.whitelist()
def selco_address_before_insert(doc,method):
    if doc.customer:
        temp_name = frappe.get_value("Customer",doc.customer,"customer_name")
        doc.address_title = doc.customer + " - " + temp_name
        doc.name = doc.customer + " - " + temp_name + " - "


@frappe.whitelist()
def send_birthday_wishes():
    list_of_bday = frappe.db.sql('SELECT salutation,employee_name,designation,branch FROM `tabEmployee` where DAY(date_of_birth) = DAY(CURDATE()) AND MONTH(date_of_birth) = MONTH(CURDATE()) AND status="Active" ',as_list=True)
    bday_wish = ""
    for employee in list_of_bday:
        bday_wish += "<b> Dear " + employee[0] + "." + employee[1].upper() + " (" + employee[2] + "," + employee[3] +  ") " + "</b>" + "<br>"
    bday_wish += "सुदिनम् सुदिना जन्मदिनम् तव | भवतु मंगलं जन्मदिनम् || चिरंजीव कुरु कीर्तिवर्धनम् | चिरंजीव कुरुपुण्यावर्धनम् || विजयी भवतु सर्वत्र सर्वदा | जगति भवतु तव सुयशगानम् || <br><br>"
    bday_wish +="​ಸೂರ್ಯನಿಂದ ನಿಮ್ಮೆಡೆಗೆ ಬರುವ ಪ್ರತಿಯೊಂದು ರಶ್ಮಿಯೂ ನಿಮ್ಮ ಬಾಳಿನ ಸಂತಸದ ಕ್ಷಣವಾಗಲಿ ಎಂದು ಹಾರೈಸುತ್ತಾ ಜನುಮ ದಿನದ  ಹಾರ್ದಿಕ ​ಶುಭಾಶಯಗಳು​.​<br><br>"
    bday_wish +="Wishing you a wonderful day on your birthday. Let this be sacred and auspicious day for you. Wish you long live with a good fame and wish you long live with your good deeds. Wish you always make ever great achievements and let the world praise you for your success. Happy Birthday to our most beloved​. ​ ​SELCO Family wishes you Happy birthday.........!!!!!​​​ <br><br>"
    bday_wish +="Best Regards<br>"
    bday_wish +="SELCO Family​​<br>"
    frappe.sendmail(
        recipients=["basawaraj@selco-india.com"],
        subject="ಹುಟ್ಟುಹಬ್ಬದ ಶುಭಾಶಯಗಳು...............!!!",
        message=bday_wish)

@frappe.whitelist()
def cleanup_si():

    for d in frappe.db.get_all("Sales Invoice",filters={"type_of_invoice": "Spare Sales Invoice"}):
        si = frappe.get_doc("Sales Invoice",d.name)
        si.cancel()
        si.delete()

    for d in frappe.db.get_all("Sales Invoice",filters={"type_of_invoice": "System Sales Invoice"}):
        si = frappe.get_doc("Sales Invoice",d.name)
        si.cancel()
        si.delete()

    for d in frappe.db.get_all("Sales Invoice",filters={"type_of_invoice": "Service Bill"}):
        si = frappe.get_doc("Sales Invoice",d.name)
        si.cancel()
        si.delete()

def cleanup_dc():
    for d in frappe.db.get_all("Delivery Note",filters={"docstatus": 2 }):
        dc = frappe.get_doc("Delivery Note",d.name)
        dc.delete()
    for d in frappe.db.get_all("Delivery Note",filters={"docstatus": 0 }):
        dc = frappe.get_doc("Delivery Note",d.name)
        dc.delete()

    for d in frappe.db.get_all("Delivery Note"):
        dc = frappe.get_doc("Delivery Note",d.name)
        dc.cancel()
        dc.delete()

def cleanup_se():
    for d in frappe.db.get_all("Stock Entry",filters={"docstatus": 0 }):
        dc = frappe.get_doc("Stock Entry",d.name)
        dc.delete()
    se_list = frappe.db.sql("select name from `tabStock Entry` where NULLIF(amended_from, '') IS NOT NULL AND docstatus AND  purpose = 'Material Transfer' ",as_list = True)
    for d in se_list:
        dc = frappe.get_doc("Stock Entry",d[0])
        dc.cancel()
        dc.delete()
