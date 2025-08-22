# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VolunteerDeploymentCriteria(Document):
	def before_submit(self):
		total_weight = 0
		child_table_name = "criteria"  
		
		if not self.get(child_table_name):
			frappe.throw("No criteria found. Please add criteria before submitting.")
			
		for criterion in self.get(child_table_name):
			total_weight += criterion.weight
		
		if total_weight != 100:
			frappe.throw(f"Total weight of all criteria must be 100. Current total: {total_weight}")
