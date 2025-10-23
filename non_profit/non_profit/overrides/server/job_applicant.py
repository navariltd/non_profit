import frappe
from frappe.model.document import Document

FIELD_GROUPS = {
    0: [
        "ward",
        "id_number",
        "passport_number",
        "number_of_dependants",
        "marital_status",
        "blood_group",
        "citizenship",
        "country_of_citizenship",
        "administrative_location",
        "sub_county",
        "county",
        "access_to_internet",
        "profession",
        "reason_to_join_krcs",
        "gender",
        "profession",
    ],
    1: [
        "languages",
        "education",
        "disabilities",
        "driving_licence",
        "certification",
        "licences",
        "additional_skills",
        "courses",
    ],
}

SKIP_CHILD_FIELDS = [
    "name",
    "parent",
    "parentfield",
    "parenttype",
    "doctype",
    "idx",
    "docstatus",
    "creation",
    "modified",
    "modified_by",
    "owner",
]

FIELD_MAP = {
    "date_of_birth": ["birth_date"],
    "mpesa_mobile_phone": ["mobile_no"],
    "phone_number": ["phone"],
}


def on_update(doc: Document, method: str) -> None:
    """
    Sync Job Applicant data to User and update screening responses, scores, and eligibility.
    """
    try:
        if doc.status != "Open":
            return

        email = doc.email_id
        if not email:
            return

        user_list = frappe.get_all("User", filters={"email": email}, limit=1)
        if not user_list:
            return

        user_doc = frappe.get_doc("User", user_list[0].name)
        has_changes = False

        for field in FIELD_GROUPS[0]:
            if not hasattr(doc, field):
                continue
            value = getattr(doc, field)
            if value is None or value == "":
                continue
            user_fields = FIELD_MAP.get(field, [field])
            for user_field in user_fields:
                if not hasattr(user_doc, user_field):
                    continue
                if getattr(user_doc, user_field, None) != value:
                    user_doc.set(user_field, value)
                    has_changes = True

        for field in FIELD_GROUPS[1]:
            try:
                if not hasattr(doc, field):
                    continue
                value = getattr(doc, field)
                if not isinstance(value, list) or not value:
                    continue
                rows = []
                for row in value:
                    row_dict = row.as_dict()
                    for skip_field in SKIP_CHILD_FIELDS:
                        row_dict.pop(skip_field, None)
                    rows.append(row_dict)
                user_doc.set(field, rows)
                has_changes = True
            except Exception:
                continue

        if has_changes:
            user_doc.save(ignore_permissions=True)
            frappe.db.commit()

        total_score = 0
        max_total_score = 0
        knock_out_failed = False

        responses = frappe.get_all(
            "Job Application Screening Responses",
            filters={"parent": doc.name},
            fields=["name", "question_id", "answer", "score_obtained"],
        )

        for resp in responses:
            question = frappe.get_doc(
                "Job Application Screening Questions",
                {"question_id": resp.question_id, "parent": doc.job_title},
            )

            score = 0
            max_score = question.max_score or 0

            if question.is_required and not resp.answer:
                score = 0
            elif resp.answer and question.expected_answer:

                score = (
                    min(max_score, question.weight)
                    if resp.answer == question.expected_answer
                    else 0
                )

            frappe.db.set_value(
                "Job Application Screening Responses",
                resp.name,
                "score_obtained",
                score,
            )

            total_score += score
            max_total_score += max_score

            if getattr(question, "is_knock_out", False) and score == 0:
                knock_out_failed = True

        screening_score_percent = 0
        if max_total_score > 0:
            screening_score_percent = (total_score / max_total_score) * 100

        doc.total_score = total_score
        doc.screening_score_percent = screening_score_percent

        if knock_out_failed:
            doc.eligibility_status = "Not Eligible"
            doc.status = "Rejected"
        else:
            if screening_score_percent >= 70:
                doc.eligibility_status = "Eligible"
            else:
                doc.eligibility_status = "Pending Review"

        doc.save(ignore_permissions=True)
        frappe.db.commit()

    except Exception:
        frappe.log_error(
            "Job Applicant -> User & Screening Sync Error",
            frappe.get_traceback(),
        )
