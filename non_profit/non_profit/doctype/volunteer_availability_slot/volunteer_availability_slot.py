# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class VolunteerAvailabilitySlot(Document):
	def validate(self):
		"""Validate the availability slot."""
		if not self.starts_on or not self.ends_on:
			frappe.throw(_("Start Time and End Time are required."))

		if self.starts_on >= self.ends_on:
			frappe.throw(_("Start Time must be before End Time."))
