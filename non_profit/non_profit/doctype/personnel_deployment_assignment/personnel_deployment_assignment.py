# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class PersonnelDeploymentAssignment(Document):
    def before_save(self):
        if not self.date:
            self.date = today()
