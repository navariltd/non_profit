import frappe


@frappe.whitelist(allow_guest=True)
def get_membership_types():

    return frappe.get_all(
        "Membership Type", fields=["name", "membership_type", "amount"]
    )


@frappe.whitelist(allow_guest=True)
def get_job_openings(filters=None, orFilters=None):
    if not filters:
        filters = {}

    jobs = frappe.get_all(
        "Job Opening",
        filters=filters,
        or_filters=orFilters,
        fields=[
            "job_title",
            "closes_on",
            "designation",
            "vacancies",
            "location",
            "employment_type",
            "company",
            "department",
            "name",
            "creation",
            "description",
            "status",
        ],
        order_by="creation desc",
    )

    for job in jobs:
        job.description = (
            frappe.utils.strip_html_tags(job.description) if job.description else ""
        )
        job.applicants = frappe.db.count("Job Applicant", {"job_title": job.name})
    return jobs


@frappe.whitelist(allow_guest=True)
def get_job_details(job):
    job_details = frappe.db.get_value(
        "Job Opening",
        job,
        [
            "job_title",
            "closes_on",
            "designation",
            "vacancies",
            "location",
            "employment_type",
            "company",
            "department",
            "name",
            "creation",
            "description",
            "status",
            "owner",
        ],
        as_dict=1,
    )

    if not job_details:
        return {}

    job_details["applicant_count"] = frappe.db.count(
        "Job Applicant", {"job_title": job_details["name"]}
    )

    if job_details.get("company"):
        company = frappe.db.get_value(
            "Company",
            job_details["company"],
            [
                "company_name",
                "company_logo",
                "website",
                "email",
                "phone_no",
            ],
            as_dict=1,
        )
        job_details.update(company or {})

    return job_details


@frappe.whitelist(allow_guest=True)
def get_regions():
    return frappe.get_all("Company", filters={"is_group": 0})


@frappe.whitelist(allow_guest=True)
def get_branches():
    return frappe.get_all("Branch")


@frappe.whitelist(allow_guest=True)
def get_user_info():
    if frappe.session.user == "Guest":
        return None

    user = frappe.db.get_value(
        "User",
        frappe.session.user,
        [
            "name",
            "email",
            "enabled",
            "user_image",
            "full_name",
            "user_type",
            "username",
        ],
        as_dict=1,
    )
    roles = frappe.get_roles(user.name)
    user["roles"] = roles

    allowed_roles = {"Volunteer", "Non Profit Member"}

    user["non_profit_member"] = "Non Profit Member" in roles
    user["volunteer"] = "Volunteer" in roles

    user["allowed"] = set(roles).issubset(allowed_roles)

    return user


@frappe.whitelist()
def get_events():
    return frappe.get_all(
        "Event",
        fields=[
            "name",
            "subject",
            "event_category",
            "event_type",
            "starts_on",
            "ends_on",
            "status",
        ],
    )


@frappe.whitelist()
def get_projects():
    return frappe.get_all(
        "Project",
        fields=[
            "name",
            "project_name",
            "status",
            "project_type",
            "is_active",
            "percent_complete",
            "priority",
            "expected_start_date",
            "expected_end_date",
        ],
    )
