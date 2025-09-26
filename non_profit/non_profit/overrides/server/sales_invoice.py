import frappe
from frappe import _
from frappe.model.document import Document
from ...utils import renew_membership


@frappe.whitelist()
def on_update(doc: Document, method: str) -> None:
    """
    Triggered on Sales Invoice update.
    If invoice has membership and outstanding_amount has changed to 0, renew the membership.
    """
    if doc.doctype != "Sales Invoice":
        return

    if not doc.membership:
        return

    if doc.outstanding_amount == 0 and doc.has_value_changed("outstanding_amount"):
        membership_id = doc.membership

        if frappe.db.exists("Membership", membership_id):
            try:
                renew_membership(membership_id)
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), "Membership Renewal Failed")
                frappe.throw(_("Failed to renew membership: {0}").format(str(e)))
