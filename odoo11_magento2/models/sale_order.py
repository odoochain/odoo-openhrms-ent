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
from odoo import fields, models

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    """Inherits the model sale.order"""
    _inherit = 'sale.order'

    magento_id = fields.Char(string="Magento Id", readonly=True,
                             store=True, help="ID of the record in magento")
    magento = fields.Boolean(string="Magento", readonly=True,
                             help="This order is linked to magento.")
    magento_status = fields.Char(string="Magento status", readonly=True,
                                 help="Status of magento")
    magento_order_date = fields.Datetime(string="Magento Order Date",
                                         help="Order date in magento")

    def action_cancel(self):
        """Supering the already existing action_cancel method and adding extra
        functionality"""
        res = super(SaleOrder, self).action_cancel()
        if self.magento:
            rec = self.env['shipment.shipment'].search([
                ('related_so_id', '=', self.id)
            ])
            if rec.id:
                rec.state = 'cancel'
        return res
