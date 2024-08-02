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
from odoo import exceptions, models, _

_logger = logging.getLogger(__name__)


class ShipmentFetchWizard(models.Model):
    """Created the model shipment.fetch.wizard"""
    _name = 'shipment.fetch.wizard'
    _inherit = 'order.fetch.wizard'
    _description = 'Shipment Fetch Wizard'

    def fetch_shipments(self):
        """Method fetch_shipments to fetch the shipments from Magento"""
        cr = self._cr
        url = '/rest/default/V1/shipments?searchCriteria=0'
        type = 'GET'
        customer_group = self.env['magento.connector'].magento_api_call(
            headers={}, url=url, type=type)
        try:
            self.fetch_orders()
            g_id = []
            items = customer_group['items']
            cr.execute("select shipment from shipment_shipment")
            g_id_dict = cr.dictfetchall()
            for rec in g_id_dict:
                g_id.append(rec['shipment'])
            split_data = [items[item:item + 5] for item in
                          range(0, len(items), 10)]
            for data in split_data:
                delay = self.with_delay(priority=1, eta=5)
                delay.create_shipments(items=data, g_id=g_id)
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        except Exception as e:
            _logger.info("Exception occured %s", e)
            raise exceptions.UserError(_("Error Occured %s") % e)

    def create_shipments(self, items, g_id):
        """Method create_shipments to create shipments from magento in odoo"""
        for item in items:
            if item['increment_id'] not in g_id:
                partner = self.env['res.partner'].search([
                    ('magento_id', '=', item['customer_id'])])
                related_so_id = self.env['sale.order'].search([
                    ('magento_id', '=', item['increment_id'])
                ])
                values = {
                    'shipment': item['increment_id'],
                    'ship_date': item['created_at'],
                    'order_id': item['order_id'],
                    'ship_to_name': partner.name,
                    'related_so_id': related_so_id.id,
                    'total_quantity': item['total_qty'],
                    'state': 'shipped'
                }
                self.env['shipment.shipment'].sudo().create(values)
