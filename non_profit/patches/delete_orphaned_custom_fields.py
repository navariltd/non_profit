import frappe


def execute():
    """
    Patch to delete Custom Fields that reference non-existing DocTypes
    in their options.
    """

    custom_fields_to_delete = [
        # Fields referencing 'Personnel Deployment Assignment'
        "Issue-personnel_deployment_request",
        "Timesheet-personnel_deployment_request",
        "Expense Claim-personnel_deployment_request",
        "Employee Advance-personnel_deployment_request",
        "Material Request-personnel_deployment_request",
        "Contract-personnel_deployment_request",
        # Fields referencing 'Personnel Deployment Request'
        "Issue-personnel_deployment_assignment",
        "Timesheet-personnel_deployment_assignment",
        "Expense Claim-personnel_deployment_assignment",
        "Employee Advance-personnel_deployment_assignment",
        "Material Request-personnel_deployment_assignment",
        "Contract-personnel_deployment_assignment",
    ]

    for field_name in custom_fields_to_delete:
        if frappe.db.exists("Custom Field", field_name):
            frappe.delete_doc(
                "Custom Field", field_name, ignore_permissions=True, force=True
            )
