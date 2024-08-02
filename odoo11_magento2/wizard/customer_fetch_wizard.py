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


class CustomerFetchWizard(models.Model):
    """Creates the model customer.fetch.wizard"""
    _name = 'customer.fetch.wizard'
    _inherit = 'order.fetch.wizard'
    _description = 'Customer Fetch Wizard'

    def fetch_customers(self):
        """Method fetch_customers to fetch customers from Magento"""
        PartnerObj = self.env['res.partner']
        cr = self._cr
        url = '/rest/V1/customers/search?searchCriteria=0'
        type = 'GET'
        customer_list = self.env['magento.connector'].magento_api_call(
            headers={}, url=url, type=type)
        try:
            items = customer_list['items']
            cr.execute("select magento_id from res_partner "
                       "where magento_id is not null")
            partners = cr.fetchall()
            partner_ids = [magento_id[0] for magento_id in
                           partners] if partners else []
            # need to fetch the complete required fields list
            # and their values
            cr.execute("select id from ir_model "
                       "where model='res.partner'")
            partner_model = cr.fetchone()
            if not partner_model:
                return
            cr.execute("select name from ir_model_fields "
                       "where model_id=%s and required=True "
                       " and store=True",
                       (partner_model[0],))
            res = cr.fetchall()
            fields_list = [i[0] for i in res if res] or []
            partner_vals = PartnerObj.default_get(fields_list)
            split_data = [items[i:i + 5] for i in
                          range(0, len(items), 10)]
            for data in split_data:
                delay = self.with_delay(priority=1, eta=5)
                delay.import_customer(items=data, partner_ids=partner_ids,
                                      partner_vals=partner_vals)
        except Exception as e:
            _logger.info("Exception occured %s", e)
            raise exceptions.UserError(_("Error Occured %s") % e)

    def import_customer(self, items, partner_ids, partner_vals):
        """Method import_customer to import customer from magento"""
        for item in items:
            if str(item['id']) not in partner_ids:
                customer_id = self.find_customer_id(
                    item,
                    partner_ids,
                    partner_vals,
                    main=True
                )
                if customer_id:
                    _logger.info("Customer is created with id %s",
                                 customer_id)
                else:
                    _logger.info("Unable to create order")

    def export_customers(self):
        """Method to import Customers from odoo to magento"""
        url = 'rest/V1/customers'
        request_type = 'POST'
        headers = {
            'Content-Type': 'application/json'
        }
        customer_data = self.get_customer_data()
        if not customer_data:
            return
        split_data = [customer_data[i:i + 5] for i in range(0, len(customer_data), 10)]
        for data in split_data:
            delay = self.with_delay(priority=1, eta=5)
            delay.magento_import_customer(customer_data=data, url=url,
                                 headers=headers, type=request_type)

    def get_customer_data(self):
        """Method get_customer_data to get the customer data to export to
        magento"""
        catalog_data = []
        customers = self.env['res.partner'].search([('magento', '=', False)])
        if customers:
            for customer in customers:
                if customer.name:
                    split_name = customer.name.split(' ')
                    first_name = split_name[0]
                    last_name = split_name[1] if len(split_name) > 1 else ' '
                    customer_list = []
                    customer_data = {
                        "email": customer.email if customer.email else f"{first_name.lower()}@gmail.com",
                        "firstname": first_name,
                        "lastname": last_name,
                        "storeId": 1,
                        "websiteId": 1
                    }
                    customer_list.append({"customer": customer_data})
                    customer_list.append(customer)
                    catalog_data.append(customer_list)
            return catalog_data or None

    def magento_import_customer(self, customer_data, url, headers, type):
        """To import customer to magento from odoo"""
        for data in customer_data:
            try:
                customer_list = self.env['magento.connector'].magento_api_call(
                    headers=headers,
                    url=url,
                    type=type,
                    data=data[0]
                )
                if customer_list.get('id'):
                    data[1].write({'magento': True})
            except Exception as e:
                pass
            _logger.info(f"{data[1].name} Customer updated in Magento")
