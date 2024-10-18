# -*- coding: utf-8 -*-

from odoo import fields, models

GENDER_SELECTION = [('male', 'Male'),
                    ('female', 'Female'),
                    ('other', 'Other')]


class HrEmployeeFamily(models.Model):
    """Table for keep employee family information"""

    _name = 'hr.employee.family'
    _description = 'HR Employee Family'

    employee_id = fields.Many2one(comodel_name='hr.employee', string="Employee",
                                  help='Select corresponding Employee',
                                  invisible=1)
    relation_id = fields.Many2one(comodel_name='hr.employee.relation',
                                  string="Relation",
                                  help="Relationship with the employee")
    member_name = fields.Char(string='Name', help="Member name in Family")
    member_contact = fields.Char(string='Contact No',
                                 help="Contact Number of the Member")
    birth_date = fields.Date(string="DOB", tracking=True,
                             help="Birth date of family member")
