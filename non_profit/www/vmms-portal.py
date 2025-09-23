import re

import frappe
from bs4 import BeautifulSoup
from frappe import _
from frappe.utils.telemetry import capture

no_cache = 1


def get_context():
    csrf_token = frappe.sessions.get_csrf_token()  
    frappe.db.commit()
    context = frappe._dict()
    context.boot = get_boot()
    context.boot.csrf_token = csrf_token  
    app_path = frappe.form_dict.get("app_path")
    favicon = frappe.db.get_single_value("Website Settings", "favicon") 
    title = frappe.db.get_single_value("Website Settings", "app_name") 
    context.title = title
    context.favicon = favicon
    capture("active_site", "non_profit")
    return context


def get_boot():
	return frappe._dict(
		{
			"frappe_version": frappe.__version__,
			"read_only_mode": frappe.flags.read_only,
			"csrf_token": frappe.sessions.get_csrf_token(),
		}
	)
