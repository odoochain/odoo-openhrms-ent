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
from odoo import exceptions, fields, models, _

_logger = logging.getLogger(__name__)


class WebsiteFetchWizard(models.Model):
    """Creates the model website.fetch.wizard"""
    _name = 'website.fetch.wizard'
    _description = 'Website Fetch Wizard'

    website_fetch_type = fields.Selection(
        [('website', 'Fetch magento websites'),
         ('stores', 'Fetch Magento stores')],
        string="Operation Type")

    def fetch_website(self):
        """Method fetch_website to check want to fetch website or store"""
        if self.website_fetch_type == 'website':
            self.fetch_websites()
        elif self.website_fetch_type == 'stores':
            self.fetch_stores()

    def fetch_websites(self):
        """Method fetch_websites to fetch websites from magento"""
        url = '/rest/V1/store/websites'
        type = 'GET'
        magento_websites = self.env['magento.connector'].magento_api_call(
            headers={}, url=url, type=type)
        try:
            items = magento_websites
            split_data = [items[item:item + 5] for item in
                          range(0, len(items), 10)]
            for data in split_data:
                delay = self.with_delay(priority=1, eta=5)
                delay.create_websites(items=data)

        except Exception as e:
            _logger.info("Exception occured %s", e)
            raise exceptions.UserError(_("Error Occured %s") % e)

    def create_websites(self, items):
        """Method create_websites to create website from magento in odoo"""
        for item in items:
            values = {
                'website_name': item['name'],
                'website_code': item['code'],
                'default_store': item['default_group_id'],
                'magento_id': item['id']
            }
            self.env['website.magento'].sudo().create(values)

    def fetch_stores(self):
        """Method fetch_stores to fetch stores from magento"""
        url = '/rest/default/V1/store/storeViews'
        type = 'GET'
        magento_stores = self.env['magento.connector'].magento_api_call(
            headers={}, url=url, type=type)
        try:
            items = magento_stores
            split_data = [items[item:item + 5] for item in
                          range(0, len(items), 10)]
            for data in split_data:
                delay = self.with_delay(priority=1, eta=5)
                delay.create_stores(items=data)
        except Exception as e:
            _logger.info("Exception occurred %s", e)
            raise exceptions.UserError(_("Error Occurred %s") % e)

    def create_stores(self, items):
        """Method to create the store from magento to odoo"""
        for item in items:
            values = {
                'store_name': item['name'],
                'store_code': item['code'],
                'default_website': item['website_id']
            }
            self.env['stores.magento'].sudo().create(values)
