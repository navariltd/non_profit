import frappe

from non_profit.setup import setup_non_profit
from datetime import timedelta


def get_company():
    company = frappe.defaults.get_defaults().company
    if company:
        return company
    else:
        company = frappe.get_list("Company", limit=1)
        if company:
            return company[0].name
    return None


def before_tests():
    # complete setup if missing
    from frappe.desk.page.setup_wizard.setup_wizard import setup_complete

    if not frappe.get_list("Company"):
        setup_complete(
            {
                "currency": "USD",
                "full_name": "Test User",
                "company_name": "Frappe Care LLC",
                "timezone": "America/New_York",
                "company_abbr": "WP",
                "industry": "Healthcare",
                "country": "United States",
                "fy_start_date": "2021-01-01",
                "fy_end_date": "2021-12-31",
                "language": "english",
                "company_tagline": "Testing",
                "email": "test@erpnext.com",
                "password": "test",
                "chart_of_accounts": "Standard",
                "domains": ["Non Profit"],
            }
        )
        setup_non_profit()


def get_current_fiscal_year():

    today = frappe.utils.today()
    fiscal_year = frappe.db.get_value(
        "Fiscal Year",
        {"year_start_date": ("<=", today), "year_end_date": (">=", today)},
    )
    return fiscal_year


def get_shift_types():
    """Get all shift types with their times"""
    return frappe.get_all("Shift Type", fields=["name", "start_time", "end_time"])


def get_dates_for_day_of_week(start_date, end_date, day_name):
    """Get all dates for a specific day of week within date range"""

    day_mapping = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    target_weekday = day_mapping.get(day_name.lower())
    if target_weekday is None:
        return []

    dates = []
    current_date = start_date

    while current_date.weekday() != target_weekday:
        current_date += timedelta(days=1)

    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=7)

    return dates


@frappe.whitelist()
def get_interviewers():
    settings = frappe.get_single("Non Profit Settings")
    allowed_roles = [r.role for r in settings.interview_roles]

    if not allowed_roles:
        return frappe.get_all("User", filters={"enabled": 1}, pluck="name")

    users_with_roles = frappe.get_all(
        "User",
        filters={
            "name": [
                "in",
                frappe.get_all(
                    "Has Role", filters={"role": ["in", allowed_roles]}, pluck="parent"
                ),
            ],
            "enabled": 1,
        },
        pluck="name",
    )

    return users_with_roles


@frappe.whitelist()
def get_expense_and_advance_approvers():

    allowed_roles = ["Expense Approver", "HR Manager"]

    users_with_roles = frappe.get_all(
        "User",
        filters={
            "name": [
                "in",
                frappe.get_all(
                    "Has Role",
                    filters={"role": ["in", allowed_roles]},
                    pluck="parent",
                ),
            ],
            "enabled": 1,
        },
        pluck="name",
    )

    return users_with_roles


def check_and_renew_membership(invoice_id: str) -> None:
    if not invoice_id or not frappe.db.exists("Sales Invoice", invoice_id):
        return

    invoice = frappe.get_doc("Sales Invoice", invoice_id)
    if not invoice.membership:
        return
    membership = frappe.get_doc("Membership", invoice.membership)
    membership.validate_membership_period()


@frappe.whitelist()
def get_companies():
    return frappe.get_all("Company", filters={"is_group": 0}, fields=["name"])
