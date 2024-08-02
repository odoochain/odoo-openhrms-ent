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
from odoo import api, fields, models

logger = logging.getLogger(__name__)


class ShipmentShipment(models.Model):
    """Creates the model shipment.shipment"""
    _name = 'shipment.shipment'

    name = fields.Char(string="Magento Shipment", readonly=True,
                       copy=False, default='Draft', help="Name of the shipment")
    shipment = fields.Char(string="Shipment", help="Id of the shipment")
    ship_date = fields.Date(string="Shipment Date", help="Date of the shipment")
    order_id = fields.Char(string="Order Id", help="Order ID of the shipment")
    related_so_id = fields.Many2one('sale.order',
                                    string='Related Order',
                                    help="The related sale order"
                                    )
    ship_to_name = fields.Char(string="Ship to Name",
                               help="Name of the ship to name")
    total_quantity = fields.Integer(String="Total Quantity",
                                    help="Total quantity of the shipment")
    state = fields.Selection(selection=[
        ('shipped', 'Shipped'),
        ('cancel', 'Cancelled')], string='Status', help="State of the shipment")

    @api.model
    def create(self, vals):
        """Supering the already existing create method and adding exrtra
        functionalities"""
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'shipment.shipment')
        return super(ShipmentShipment, self).create(vals)
