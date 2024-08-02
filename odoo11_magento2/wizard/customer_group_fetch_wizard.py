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
from odoo import models, exceptions, _

_logger = logging.getLogger(__name__)


class CustomerGroupFetchWizard(models.Model):
    """Creates the model customer_group.fetch.wizard"""
    _name = 'customer_group.fetch.wizard'
    _inherit = 'order.fetch.wizard'
    _description = 'Customer Group Fetch Wizard'

    def fetch_customer_group(self):
        """Method fetch_customer_group to fetch customer groups from Magento"""
        cr = self._cr
        url = '/rest/V1/customerGroups/search?searchCriteria=0'
        type = 'GET'
        customer_group = self.env['magento.connector'].magento_api_call(
            headers={}, url=url, type=type)
        try:
            items = customer_group['items']
            cr.execute("select group_id from customer_group")
            g_id = cr.fetchall()
            g_ids = [i[0] for i in g_id] if g_id else []
            split_data = [items[item:item + 5] for item in range(0, len(items), 10)]
            for data in split_data:
                delay = self.with_delay(priority=1, eta=5)
                delay.create_customer_groups(items=data, g_ids=g_ids)
        except Exception as e:
            _logger.info("Exception occured %s", e)
            raise exceptions.UserError(_("Error Occured %s") % e)

    def create_customer_groups(self, items, g_ids):
        """Method create_customer_groups to create the customer groups to
        odoo from magento"""
        for item in items:
            if g_ids != []:
                _logger.info("ALL IMPORTED")
            else:
                values = {
                    'group_id': item['id'],
                    'group': item['code'],
                    'tax_class': item['tax_class_name'],
                    'magento': True
                }
                self.env['customer.group'].sudo().create(values)

    def export_customer_groups(self):
        """Method to import Customers from odoo to magento"""
        url = 'rest/V1/customerGroups'
        request_type = 'POST'
        headers = {
            'Content-Type': 'application/json'
        }
        customer_groups_data = self.get_customer_groups_data()
        if not customer_groups_data:
            return
        split_data = [customer_groups_data[i:i + 5] for i in
                      range(0, len(customer_groups_data), 10)]
        for data in split_data:
            delay = self.with_delay(priority=1, eta=5)
            delay.magento_import_customer_groups(groups_data=data, url=url,
                                  headers=headers, type=request_type)

    def get_customer_groups_data(self):
        """Method get_customer_groups_data to get the customer groups data to
        export to magento"""
        customer_groups = self.env['customer.group'].search([('magento', '=', False)])
        customer_groups_data = []
        if customer_groups:
            for customer_group in customer_groups:
                groups_list = []
                groups_data = {
                    "code": customer_group.group,
                    "tax_class_id": 3
                }
                groups_list.append({"group": groups_data})
                groups_list.append(customer_group)
                customer_groups_data.append(groups_list)
            return customer_groups_data or None

    def magento_import_customer_groups(self, groups_data, url, headers, type):
        """To import customer to magento from odoo"""
        for data in groups_data:
            try:
                group_list = self.env['magento.connector'].magento_api_call(
                    headers=headers,
                    url=url,
                    type=type,
                    data=data[0]
                )
                if group_list.get('id'):
                    data[1].write({
                        'group_id': group_list.get('id'),
                        'tax_class': 'Retail Customer'
                    })
            except Exception as e:
                pass
            _logger.info(f"{data[1].group} Customer Groups updated in Magento")
