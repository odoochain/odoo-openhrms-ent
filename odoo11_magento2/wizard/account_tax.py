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


class AccountTaxWizard(models.Model):
    """Creates the model account.wizard.wizard"""
    _name = 'account.tax.wizard'
    _description = 'Account Tax Wizard'

    def import_taxes(self):
        """Method fetch_taxes to fetch taxes from magento."""
        cr = self._cr
        taxUrl = '/rest/V1/taxRules/search?searchCriteria=0'
        type = 'GET'
        taxRules = self.env['magento.connector'].magento_api_call(headers={},
                                                                  url=taxUrl,
                                                                  type=type)
        for tax_rule in taxRules['items']:
            cr.execute(
                """SELECT id FROM account_tax WHERE magento_id = '%s'""" %tax_rule['id']
            )
            rates = cr.fetchall()
            if not rates:
                tax_val = {}
                group_id = tax_rule['tax_rate_ids'][0]
                taxRates = self.env['magento.connector'].magento_api_call(
                    headers={},
                    url='/rest/V1/taxRates/search?searchCriteria=0',
                    type=type)
                tax_grp_val = {}
                for tax_rate in taxRates['items']:
                    taxrate = tax_rate
                    exist_id = self.env['account.tax.group'].search([
                        ('magento_id', '=', group_id)]).id
                    if tax_rate['id'] == group_id and not exist_id:
                        tax_grp_val.update({
                            'name': tax_rate['code'],
                            'country_id': self.env.company.id,
                            'magento': True,
                            'magento_id': tax_rate['id'],
                        })
                        self.env['account.tax.group'].sudo().create(tax_grp_val)
                tax_val.update({
                    'magento_id': tax_rule['id'],
                    'name': tax_rule['code'],
                    'type_tax_use': 'sale',
                    'amount_type': 'percent',
                    'amount': taxrate['rate'],
                    'magento': True,
                    'price_include': True,
                    'include_base_amount': True,
                    'tax_group_id': self.env['account.tax'].search([], limit=1).id,
                })
                self.env['account.tax'].sudo().create(tax_val)

    def export_taxes(self):
        """Method export_taxes to export taxes from odoo."""
        url = 'rest/V1/taxRules'
        request_type = 'POST'
        headers = {
            'Content-Type': 'application/json'
        }
        tax_data = self.get_tax_data()
        if not tax_data:
            return
        split_data = [tax_data[i:i + 5] for i in range(0, len(tax_data), 10)]
        for data in split_data:
            delay = self.with_delay(priority=1, eta=5)
            delay.magento_import_taxes(tax_data=data, url=url,
                                  headers=headers, type=request_type)

    def get_tax_data(self):
        """Method get_invoices_data to get the invoices data to import to magento"""
        taxes = self.env['account.tax'].search([('magento', '=', False)])
        taxes_data = []
        if taxes:
            for tax in taxes:
                tax_group = self.env['account.tax.group'].browse(tax['tax_group_id'].id)
                tax_rate_id = tax_group.magento_id
                if not tax_group.magento:
                    tax_groups_data = []
                    tax_group_data = {
                        "taxRate": {
                            "code": tax_group['name'],
                            "rate": 10,
                            "tax_country_id": "US",
                            "tax_region_id": 12,
                            "tax_postcode": "*",
                        }
                    }
                    tax_groups_data.append(tax_group_data)
                    tax_groups_data.append(tax_group)
                    if not tax_groups_data:
                        return
                    split_data = [tax_groups_data[i:i + 5] for i in
                                  range(0, len(tax_groups_data), 10)]
                    for data in split_data:
                        tax_group_list = self.env['magento.connector'].magento_api_call(
                            headers={
                                'Content-Type': 'application/json'
                            },
                            url='rest/V1/taxRates',
                            type='POST',
                            data=data[0]
                        )
                        tax_rate_id = tax_group_list.get('id')
                        if tax_group_list.get('id'):
                            data[1].write({
                                'magento': True,
                                'magento_id': tax_group_list.get('id')
                            })
                tax_list = []
                tax_data = {
                    "rule": {
                        "code": tax['name'],
                        "priority": 2,
                        "position": 2,
                        "calculate_subtotal": True,
                        "customer_tax_class_ids": [3],
                        "product_tax_class_ids": [2],
                        "tax_rate_ids": [tax_rate_id]
                    }
                }
                tax_list.append(tax_data)
                tax_list.append(tax)
                taxes_data.append(tax_list)
            return taxes_data or None

    def magento_import_taxes(self, tax_data, url, headers, type):
        """To import taxes to magento from odoo"""
        for data in tax_data:
            try:
                tax_list = self.env['magento.connector'].magento_api_call(
                    headers=headers,
                    url=url,
                    type=type,
                    data=data[0]
                )
                if tax_list.get('id'):
                    data[1].write({
                        'magento': True,
                        'magento_id': str(tax_list.get('id'))
                    })
            except Exception as e:
                pass
            _logger.info(f"{data[1].name} Taxes updated in Magento")
