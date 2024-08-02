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
{
    'name': 'Magento-2.3 Connector',
    'version': '17.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Synchronize data between Odoo and Magento',
    'description': """The Odoo 17 Magento 2.3 connector helps businesses 
    synchronize data between Odoo and Magento 2.3, improving efficiency and 
    accuracy in managing sales, inventory, and customer information across both 
    platforms.""",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://cybrosys.com',
    'depends': ['sale_management', 'stock', 'queue_job_cron_jobrunner'],
    'data': [
        'security/odoo11_magento2_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'data/ir_sequence_data.xml',
        'views/account_move_views.xml',
        'views/account_tax_groups_views.xml',
        'views/account_tax_views.xml',
        'views/customer_group_views.xml',
        'views/magento_dashboard_views.xml',
        'views/product_template_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/shipment_shipment_views.xml',
        'views/stores_magento_views.xml',
        'views/website_magento_views.xml',
        'wizard/order_fetch_wizard_views.xml',
        'wizard/account_tax_groups_views.xml',
        'wizard/account_tax_views.xml',
        'wizard/credit_notes_fetch_wizard_views.xml',
        'wizard/customer_fetch_wizard_views.xml',
        'wizard/customer_group_fetch_wizard_views.xml',
        'wizard/products_fetch_wizard_views.xml',
        'wizard/shipment_fetch_wizard_views.xml',
        'wizard/update_stock_wizard_views.xml',
        'wizard/website_fetch_wizard_views.xml',
        'views/magento_menu_items.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'odoo11_magento2/static/src/css/magento_dashboard.css',
            'odoo11_magento2/static/src/xml/dashboard.xml',
            "odoo11_magento2/static/src/js/dashboard.js"
        ],
    },
    'images': ['static/description/banner.jpg'],
    'license': 'OPL-1',
    'price': 49,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': True,
}