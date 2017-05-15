// Copyright (c) 2016, Selco and contributors
// For license information, please see license.txt

frappe.query_reports["Lead Details with Daily Columns"] = {
	"filters": [
		{
	"fieldname": "fiscal_year",
	"label": __("Fiscal Year"),
	"fieldtype": "Link",
	"options": "Fiscal Year",
	default: "2017-2018"
	},
	{
		"fieldname":"month_number",
		"label": __("Month"),
		"fieldtype": "Select",
		"options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
		"default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
			"Dec"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
	}

],
/*
	"formatter":function (row, cell, value, columnDef, dataContext, default_formatter) {
		value = default_formatter(row, cell, value, columnDef, dataContext);
		if (dataContext.id == "Daily Total")
		{
			value = "<span style='font-weight:bold'>" + value + "</span>";
		}
	 return value;
}

/*"formatter": function(row, cell, value, columnDef, dataContext, default_formatter) {
    value = default_formatter(row, cell, value, columnDef, dataContext);
    if (columnDef.id == "D10") {
        if (dataContext.D10 < 1) {
            value = "<span style='color:red'>" + value + "</span>";
        }
				else if (dataContext.D10 == 1)
				{
					value = "<span style='color:black'>" + value + "</span>";
				}
				else if (dataContext.D10 > 1)
				{
					value = "<span style='color:green;font-weight:bold'>" + value + "</span>";
				}
    }
		if (columnDef.id == "D15") {
        if (dataContext.D15 < 1) {
            value = "<span style='color:red;font-weight:bold'>" + value + "</span>";
        }
    }
    return value;
}
*/
/*
"formatter":function (row, cell, value, columnDef, dataContext, default_formatter) {
    value = default_formatter(row, cell, value, columnDef, dataContext);
//	if (columnDef.id != "Branch" && columnDef.id != "Senior Manger" && columnDef.id != "Name of SE" && columnDef.id != "SE Contact Number" && columnDef.id != "Designation") {
		if(dataContext.Branch == "Daily Total"){
		var $value = $(value).css("font-weight", "bold");
		$value = $(value).css("color", "blue");
					value = $value.wrap("<p></p>").parent().html();
					//value = "<span style='color:blue;font-weight:bold'>" + value + "</span>";
				}
				//}
	return value;
}*/
}
