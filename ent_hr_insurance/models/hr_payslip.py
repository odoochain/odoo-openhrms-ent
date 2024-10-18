# -*- coding: utf-8 -*-
from odoo import models


class InsuranceRuleInput(models.Model):

    """Hr Payslip model is used to add custom fields and methods."""
    _inherit = 'hr.payslip'

    def get_inputs(self, contract_ids, date_from, date_to):

        """Returns the amount of deduction per month"""
        res = super(InsuranceRuleInput, self).get_inputs(contract_ids,
                                                         date_from, date_to)
        contract_obj = self.env['hr.contract']
        for i in contract_ids:
            if contract_ids[0]:
                emp_id = contract_obj.browse(i[0].id).employee_id
                for result in res:
                    if emp_id.deduced_amount_per_month != 0:
                        if result.get('code') == 'INSUR':
                            result['amount'] = emp_id.deduced_amount_per_month
        return res