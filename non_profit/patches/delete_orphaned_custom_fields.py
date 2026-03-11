import frappe


def execute():
    """
    Patch to delete Custom Fields that reference non-existing DocTypes
    in their options.
    """

    custom_fields_to_check = [
        # Fields referencing 'Personnel Deployment Assignment'
        {"dt": "Issue", "fieldname": "personnel_deployment_request"},
        {"dt": "Timesheet", "fieldname": "personnel_deployment_request"},
        {"dt": "Expense Claim", "fieldname": "personnel_deployment_request"},
        {"dt": "Employee Advance", "fieldname": "personnel_deployment_request"},
        {"dt": "Material Request", "fieldname": "personnel_deployment_request"},
        {"dt": "Contract", "fieldname": "personnel_deployment_request"},
        # Fields referencing 'Personnel Deployment Request'
        {"dt": "Issue", "fieldname": "personnel_deployment_assignment"},
        {"dt": "Timesheet", "fieldname": "personnel_deployment_assignment"},
        {"dt": "Expense Claim", "fieldname": "personnel_deployment_assignment"},
        {"dt": "Employee Advance", "fieldname": "personnel_deployment_assignment"},
        {"dt": "Material Request", "fieldname": "personnel_deployment_assignment"},
        {"dt": "Contract", "fieldname": "personnel_deployment_assignment"},
    ]

    for field in custom_fields_to_check:
        dt = field["dt"]
        fieldname = field["fieldname"]

        custom_field_name = frappe.db.get_value(
            "Custom Field", {"dt": dt, "fieldname": fieldname}, "name"
        )

        if not custom_field_name:
            frappe.logger().info(
                f"Patch: Custom Field '{fieldname}' on '{dt}' not found — skipping."
            )
            continue

        options = frappe.db.get_value("Custom Field", custom_field_name, "options")

        if not options:
            frappe.logger().info(
                f"Patch: Custom Field '{fieldname}' on '{dt}' has no options — skipping."
            )
            continue

        referenced_doctype_exists = frappe.db.exists("DocType", options)

        if not referenced_doctype_exists:
            frappe.delete_doc(
                "Custom Field", custom_field_name, ignore_permissions=True, force=True
            )

    frappe.db.commit()
