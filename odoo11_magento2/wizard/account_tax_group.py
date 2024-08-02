# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###############################################################################
import logging
from odoo import models

_logger = logging.getLogger(__name__)


class AccountTaxGroupWizard(models.Model):
    """Creates the model account.tax.group.wizard"""
    _name = 'account.tax.group.wizard'
    _description = 'Account Tax Group Wizard'

    def import_tax_group(self):
        """Method fetch_tax_group to fetch tax groups from magento."""
        cr = self._cr
        taxUrl = '/rest/V1/taxRates/search?searchCriteria=0'
        type = 'GET'
        taxRates = self.env['magento.connector'].magento_api_call(headers={},
                                                                  url=taxUrl,
                                                                  type=type)
        for tax_rate in taxRates['items']:
            cr.execute(
                """SELECT id FROM account_tax_group WHERE magento_id = '%s'""" %tax_rate['id']
            )
            rates = cr.fetchall()
            if not rates:
                tax_val = {}
                tax_val.update({
                    'name': tax_rate['code'],
                    'country_id': self.env.company.id,
                    'magento': True,
                    'magento_id': tax_rate['id'],
                })
                self.env['account.tax.group'].sudo().create(tax_val)

    def export_tax_group(self):
        """Method export_tax_group to export tax groups from odoo."""
        url = 'rest/V1/taxRates'
        request_type = 'POST'
        headers = {
            'Content-Type': 'application/json'
        }
        tax_group_data = self.get_tax_group_data()
        if not tax_group_data:
            return
        split_data = [tax_group_data[i:i + 5] for i in range(0, len(tax_group_data), 10)]
        for data in split_data:
            delay = self.with_delay(priority=1, eta=5)
            delay.magento_import_tax_group(tax_group_data=data, url=url,
                                       headers=headers, type=request_type)

    def get_tax_group_data(self):
        """Method get_invoices_data to get the invoices data to
                import to magento"""
        tax_group = self.env['account.tax.group'].search([('magento', '=', False)])
        tax_groups_data = []
        if tax_group:
            for tax in tax_group:
                tax_group_list = []
                tax_group_data = {
                    "taxRate": {
                        "code": tax['name'],
                        "rate": 10,
                        "tax_country_id": "US",
                        "tax_region_id": 12,
                        "tax_postcode": "*",
                    }
                }
                tax_group_list.append(tax_group_data)
                tax_group_list.append(tax)
                tax_groups_data.append(tax_group_list)
            return tax_groups_data or None

    def magento_import_tax_group(self, tax_group_data, url, headers, type):
        """To import taxes to magento from odoo"""
        for data in tax_group_data:
            try:
                tax_group_list = self.env['magento.connector'].magento_api_call(
                    headers=headers,
                    url=url,
                    type=type,
                    data=data[0]
                )
                if tax_group_list.get('id'):
                    data[1].write({
                        'magento': True,
                        'magento_id': str(tax_group_list.get('id'))
                    })
            except Exception as e:
                pass
            _logger.info(f"{data[1].group} Invoices Groups updated in Magento")
