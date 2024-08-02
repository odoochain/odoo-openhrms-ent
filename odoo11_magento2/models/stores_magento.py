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
from odoo import api, fields, models


class StoresMagento(models.Model):
    """Creates the model called stores.magento"""
    _name = 'stores.magento'

    name = fields.Char(string="Magento Store", readonly=True,
                       copy=False, default='Draft', help="Name of the store")
    store_name = fields.Char(string="Website Name",
                             help="Name of the website of the store")
    store_code = fields.Char(string="Code", help="Code of the store")
    default_website = fields.Char(string="Default Website",
                                  help="Default website of the store")

    @api.model
    def create(self, vals):
        """Supering the already existing create method and adding extra
        functionalities"""
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'stores.magento')
        return super(StoresMagento, self).create(vals)
