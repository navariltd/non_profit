# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.contacts.address_and_contact import load_address_and_contact
from frappe.model.document import Document


class Donor(Document):
	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self)

	def validate(self):
		from frappe.utils import validate_email_address
		if self.email:
			validate_email_address(self.email.strip(), True)

	def after_insert(self):
		settings = frappe.get_doc("Changemakers Settings")

		if settings.generate_customer_when_donor_is_created:
			self.create_customer()

	@frappe.whitelist()
	def create_customer(self) :
		if self.customer:
			return
		
		if not frappe.db.exists("Customer Group", "Beneficiary"):
			customer_group = frappe.new_doc("Customer Group")
			customer_group.customer_group_name = "Beneficiary"
			customer_group.flags.ignore_permissions = True
			customer_group.insert()

		customer = frappe.new_doc("Customer")
		customer.customer_name = self.donor_name
		customer.customer_type = "Individual"
		customer.customer_group = "Beneficiary"

		customer.flags.ignore_permissions = True
		customer.insert()
		self.customer = customer.name
		self.save()
		return customer.name
