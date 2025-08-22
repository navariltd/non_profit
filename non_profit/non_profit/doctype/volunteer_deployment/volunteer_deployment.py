# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class VolunteerDeployment(Document):
    def validate(self):
        self.validate_volunteer_count()
    
    def validate_volunteer_count(self):
        """Validate that assigned volunteers don't exceed required count"""
        if self.number_of_volunteers_required and len(self.volunteers) > self.number_of_volunteers_required:
            frappe.throw(_("Number of assigned volunteers ({0}) exceeds required count ({1})").format(
                len(self.volunteers), self.number_of_volunteers_required
            ))

@frappe.whitelist()
def get_available_volunteers(company, branch, deployment=None):
    """
    Fetch available volunteers matching company, branch and status
    """ 
    volunteers = frappe.get_all("Volunteer",
        filters={
            'company': company,
            'branch': branch,
            'status': 'Available',
        },
        fields=['name as volunteer', 'volunteer_name', 'status']
    )
    
    for volunteer in volunteers:
        skills = frappe.get_all("Volunteer Skill",
            filters={'parent': volunteer['volunteer']},
            fields=['volunteer_skill'],
            pluck='volunteer_skill'
        )
        volunteer['skills'] = ', '.join(skills) if skills else 'No skills listed'

    return volunteers

