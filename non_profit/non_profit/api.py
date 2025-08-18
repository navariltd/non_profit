import frappe


@frappe.whitelist(allow_guest=True)
def get_membership_types():

    return frappe.get_all(
        "Membership Type", fields=["name", "membership_type", "amount"]
    )
