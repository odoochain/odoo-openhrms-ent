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
from odoo import fields, models


class ProductProduct(models.Model):
    """Inherits the model product.product"""
    _inherit = 'product.product'

    magento_categ_ids = fields.One2many('magento.product.category',
                                        'product_id',
                                        string="Magento Categories",
                                        readonly=True,
                                        help="ID's for product categories in "
                                             "Magento")
    magento = fields.Boolean(string="Magento", readonly=True, store=True,
                             help="This product is created from magento.",
                             related='product_tmpl_id.magento')
    magento_id = fields.Char(string="Magento id of the product",
                             store=True, help="ID of the product in magento")
    magento_type = fields.Char(string="Type of Product in Magento",
                               readonly=True,
                               help="Type of the product in magento")
