import frappe


@frappe.whitelist(allow_guest=True)
def get_membership_types():

    return frappe.get_all(
        "Membership Type", fields=["name", "membership_type", "amount"]
    )


@frappe.whitelist(allow_guest=True)
def get_regions():
    return frappe.get_all("Company", filters={"is_group": 0})


@frappe.whitelist(allow_guest=True)
def get_branches():
    return frappe.get_all("Branch")