# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api


class EmployeeInsurance(models.Model):
    """Class representing an employee insurance account and is responsible
    for managing the employee coverage"""
    _name = 'hr.insurance'
    _description = 'HR Insurance'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  required=True, help="Employee")
    policy_id = fields.Many2one('insurance.policy', string='Policy',
                                required=True, help="Policy")
    amount = fields.Float(string='Premium', required=True, help="Policy amount")
    sum_insured = fields.Float(string="Sum Insured", required=True,
                               help="Insured sum")
    policy_coverage = fields.Selection(
        [('monthly', 'Monthly'), ('yearly', 'Yearly')],
        required=True, default='monthly',
        string='Policy Coverage', help="During of the policy")
    date_from = fields.Date(string='Date From',
                            default=time.strftime('%Y-%m-%d'), readonly=True,
                            help="Start date")
    date_to = fields.Date(string='Date To', readonly=True, help="End date",
                          default=str(
                              datetime.now() + relativedelta.relativedelta(
                                  months=+1, day=1, days=-1))[:10])
    state = fields.Selection([('active', 'Active'),
                              ('expired', 'Expired'), ],
                             default='active', string="State",
                             compute='get_status')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 help="Company",
                                 default=lambda self: self.env.user.company_id)

    def get_status(self):
        """Return the status of the instance."""
        current_date = datetime.now().date()
        for record in self:
            date_from = record.date_from.date()
            date_to = record.date_to.date()
            if date_from <= current_date <= date_to:
                record.state = 'active'
            else:
                record.state = 'expired'

    @api.constrains('policy_coverage')
    @api.onchange('policy_coverage')
    def get_policy_period(self):
        """Returns the period"""
        if self.policy_coverage == 'monthly':
            self.date_to = str(
                datetime.now() + relativedelta.relativedelta(months=+1, day=1,
                                                             days=-1))[:10]
        if self.policy_coverage == 'yearly':
            self.date_to = str(
                datetime.now() + relativedelta.relativedelta(months=+12))[:10]
