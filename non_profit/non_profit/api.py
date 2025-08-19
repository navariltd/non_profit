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
		job.description = frappe.utils.strip_html_tags(job.description) if job.description else ""
		job.applicants = frappe.db.count("Job Applicant", {"job_title": job.name})
	return jobs