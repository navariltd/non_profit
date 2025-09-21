import frappe
from frappe.model.document import Document
from frappe import _


def validate(doc: Document, method: str) -> None:
    if doc.opportunity_type == "Internal" and doc.designation:
        designation = frappe.get_doc("Designation", doc.designation)
        if not designation.skills or len(designation.skills) == 0:
            frappe.throw(
                _("The selected Designation must have at least one Skill entry.")
            )
