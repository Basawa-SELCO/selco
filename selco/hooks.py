# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "selco"
app_title = "Selco"
app_publisher = "Selco"
app_description = "Selco"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "basawaraj@selco-india.com"
app_version = "0.0.1"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/selco/css/selco.css"
# app_include_js = "/assets/selco/js/selco.js"

# include js, css files in header of web template
# web_include_css = "/assets/selco/css/selco.css"
# web_include_js = "/assets/selco/js/selco.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#    "Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "selco.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "selco.install.before_install"
# after_install = "selco.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "selco.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#     "Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#     "Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#     "*": {
#         "on_update": "method",
#         "on_cancel": "method",
#         "on_trash": "method"
#    }
# }

doc_events = {

    "Issue": {
         "validate": "selco.selco.doctype.selco_customizations.selco_customizations.selco_issue_updates"
    },
    "Warranty Claim": {
         "validate": "selco.selco.doctype.selco_customizations.selco_customizations.selco_warranty_claim_updates"
    },
    "Delivery Note": {
         "before_insert": "selco.selco.doctype.selco_customizations.selco_customizations.selco_delivery_note_updates"
    },
    "Material Request": {
         "before_insert": "selco.selco.doctype.selco_customizations.selco_customizations.selco_material_request_updates"
    },
    "Purchase Receipt": {
         "before_insert": "selco.selco.doctype.selco_customizations.selco_customizations.selco_purchase_receipt_updates"
    },
    "Stock Entry": {
         "before_insert": "selco.selco.doctype.selco_customizations.selco_customizations.selco_stock_entry_updates"
    },
    "Customer": {
         "validate": "selco.selco.doctype.selco_customizations.selco_customizations.selco_customer_updates"
    },
    "Customer": {
         "before_insert": "selco.selco.doctype.selco_customizations.selco_customizations.selco_customer_before_insert"
    }
 }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#     "all": [
#         "selco.tasks.all"
#     ],
#     "daily": [
#         "selco.tasks.daily"
#     ],
#     "hourly": [
#         "selco.tasks.hourly"
#     ],
#     "weekly": [
#         "selco.tasks.weekly"
#     ]
#     "monthly": [
#         "selco.tasks.monthly"
#     ]
# }

# Testing
# -------

# before_tests = "selco.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
#     "frappe.desk.doctype.event.event.get_events": "selco.event.get_events"
# }
