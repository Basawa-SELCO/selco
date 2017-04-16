// Copyright (c) 2016, Selco and contributors
// For license information, please see license.txt

frappe.query_reports["Pending IBM Master Report"] = {
	"filters": [
		{
				"fieldname":"godown",
				"label": __("Godown"),
				"fieldtype": "Select",
				"options": "All Godowns\nBangalore Godown\nManipal Godown\nDharwad Godown",
		}

	]
}
