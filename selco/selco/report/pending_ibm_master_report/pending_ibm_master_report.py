# Copyright (c) 2013, Selco and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json

def execute(filters=None):
    columns, data = [], []
    columns = get_columns()
    data = get_data(filters)
    data1 = []
    for d in data:
        row = [d.selco_date,d.name,d.branch,d.item_name,d.item_code,d.description,d.qty,d.dispatched_quantity,d.qty-d.dispatched_quantity,d.godown_email_id]
        data1.append(row)
    return columns, data1

def get_columns():
    columns = [
        ("Date")+":Date:100",
        ("IBM Number")+":Link/Material Request:150",
        ("Branch")+":Link/Branch:100",
        ("Item name")+"Data:100",
        ("Item code")+"Link/Item Code:100",
        ("Description")+"Data:100",
        ("Quantity Requested")+"Int:100",
        ("Dispatched")+"Int:100",
        ("To be Dispatched")+"Int:100",
        ("Email ID")+"Date:100"
        ]
    return columns

def get_data(filters):
    conditions = ""
    if filters.get("godown"):
        choosen_godown = filters.get("godown")
        if choosen_godown == "All Godowns":
            conditions = ""
        elif choosen_godown == "Bangalore Godown":
            #conditions += " and A.godown_email_id = '%s'" % frappe.db.escape(filters.get("godown"), percent=False)
            conditions += ' and A.godown_email_id = "bangalore_godown@selco-india.com"'
        elif choosen_godown == "Manipal Godown":
            conditions += ' and A.godown_email_id = "southgodown@selco-india.com"'
        elif choosen_godown == "Dharwad Godown":
            conditions += ' and A.godown_email_id = "northgodown@selco-india.com"'
    return frappe.db.sql("""SELECT A.selco_date,A.name,A.branch,B.item_name,B.item_code,B.description,B.qty,B.dispatched_quantity,A.godown_email_id,A.workflow_state from `tabMaterial Request` A  JOIN `tabMaterial Request Item` B ON A.name = B.parent AND B.qty-B.dispatched_quantity > 0  AND  A.workflow_state
IN("Approved - IBM","Partially Dispatched From Godown - IBM") %s""" % (conditions),as_dict=True)
