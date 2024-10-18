# -*- coding: utf-8 -*-
from odoo import fields, models


class HrContract(models.Model):
    """ Model adding notice period days in hr_contract. """
    _inherit = 'hr.contract'

    def _get_default_notice_days(self):
        """ Method for return notice days. """
        if self.env['ir.config_parameter'].sudo().get_param(
                'hr_resignation.notice_period'):
            return self.env['ir.config_parameter'].sudo().get_param(
                            'hr_resignation.no_of_days')
        else:
            return 0

    notice_days = fields.Integer(string="Notice Period",
                                 help="Notice Days",
                                 default=_get_default_notice_days)
