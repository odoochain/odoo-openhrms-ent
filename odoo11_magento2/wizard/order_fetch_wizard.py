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


class OrderFetchWizard(models.Model):
    """Creates the model order.fetch.wizard"""
    _name = 'order.fetch.wizard'
    _description = 'Order Fetch Wizard'

    def find_customer_id(self, item, ids, partner_vals, main=False):
        """Method find_customer_id to get the customer"""
        cr = self._cr
        id_key = 'customer_id'
        pre_key = 'customer_'
        if main:
            id_key = 'id'
            pre_key = ''
        if item.get(id_key) and str(item[id_key]) in ids:
            cr.execute("select id from res_partner "
                       "where magento_id=%s",
                       (str(item[id_key]),))
            res = cr.fetchone()
            return res and res[0] or None
        else:
            if item.get('customer_is_guest'):
                cr.execute("select id from res_partner "
                           "where email=%s",
                           (str(item.get('customer_email')),))
                res = cr.fetchone()
                if res:
                    return res and res[0] or None
            partner_vals['name'] = (item.get(
                pre_key + 'firstname') or '') + " " + (
                                           item.get(pre_key + 'lastname') or '')
            partner_vals['magento'] = True
            partner_vals['active'] = True
            partner_vals['magento_id'] = item.get(id_key)
            partner_vals['email'] = item.get('email') or item.get(
                'customer_email')
            if item.get('addresses'):
                partner_vals['phone'] = item['addresses'][0]['telephone']
                partner_vals['city'] = item['addresses'][0]['city']
                partner_vals['country_id'] = self.env['res.country'].search(
                    [('code', '=', item['addresses'][0]['country_id'])]).id
                partner_vals['zip'] = item['addresses'][0]['postcode']
                partner_vals['street'] = item['addresses'][0]['street'][0]
                try:
                    partner_vals['street2'] = item['addresses'][0]['street'][1]
                except:
                    pass
            if item.get('billing_address'):
                partner_vals['phone'] = item['billing_address']['telephone']
                partner_vals['city'] = item['billing_address']['city']
                partner_vals['country_id'] = self.env['res.country'].search(
                    [('code', '=', item['billing_address']['country_id'])]).id
                partner_vals['zip'] = item['billing_address']['postcode']
                partner_vals['street'] = item['billing_address']['street'][0]
                try:
                    partner_vals['street2'] = item['billing_address']['street'][
                        1]
                except:
                    pass
            query_cols = self.fetch_query(partner_vals)
            query_str = "insert into res_partner (" + \
                        query_cols + ") values %s RETURNING id"
            cr.execute(query_str,
                       (tuple(partner_vals.values()),))
            res = cr.fetchone()
            return res and res[0] or None

    def fetch_query(self, vals):
        """Constructing the query, from the provided column names"""
        query_str = ""
        if not vals:
            return
        for col in vals:
            query_str += " " + str(col) + ","
        return query_str[:-1]

    def fetch_orders(self):
        """Method fetch_orders to fetch the orders"""
        PartnerObj = self.env['res.partner']
        OrderObj = self.env['sale.order']
        ProductObj = self.env['product.product']
        cr = self._cr
        self.env['account.tax.wizard'].import_taxes()
        self.env['account.tax.group.wizard'].import_tax_group()
        # We are fetching all the records without checking that
        # they already exist or not, because, if we try to setup a filter,
        # then the url may become too long and cause some other errors
        url = '/rest/V1/orders?searchCriteria=0'
        type = 'GET'
        order_list = self.env['magento.connector'].magento_api_call(headers={},
                                                                    url=url,
                                                                    type=type)
        try:
            items = order_list['items']
            cr.execute("select magento_id from sale_order where magento_id is not null")
            orders = cr.fetchall()
            order_ids = [i[0] for i in orders] if orders else []
            cr.execute("select magento_id from res_partner "
                       "where magento_id is not null")
            partners = cr.fetchall()
            partner_ids = [i[0] for i in partners] if partners else []
            # Need to fetch the complete required fields list and their values
            cr.execute("select id from ir_model "
                       "where model='sale.order'")
            order_model = cr.fetchone()
            if not order_model:
                return
            cr.execute("select name from ir_model_fields "
                       "where model_id=%s and required=True and store=True",
                       (order_model[0],))
            res = cr.fetchall()
            fields_list = [i[0] for i in res if res] or []
            order_vals = OrderObj.default_get(fields_list)
            cr.execute("select id from ir_model where model='res.partner'")
            partner_model = cr.fetchone()
            if not partner_model:
                return
            cr.execute("select name from ir_model_fields "
                       "where model_id=%s and required=True and store=True",
                       (partner_model[0],))
            res = cr.fetchall()
            fields_list = [i[0] for i in res if res] or []
            partner_vals = PartnerObj.default_get(fields_list)
            order_num = 0
            split_data = [items[item:item + 5] for item in range(0, len(items), 10)]
            for data in split_data:
                delay = self.with_delay(priority=1, eta=5)
                delay.import_orders(items=data, order_ids=order_ids,
                                    partner_ids=partner_ids,
                                    partner_vals=partner_vals,
                                    order_vals=order_vals,
                                    ProductObj=ProductObj, OrderObj=OrderObj)
            _logger.info("%s orders created", order_num)
            return {
                'type': 'ir.actions.client',
                'tag': 'reload'
            }
        except Exception as e:
            _logger.info("Exception occured %s", e)
            raise exceptions.UserError(_("Error Occured 4 %s") % e)

    def import_orders(self, items, partner_ids, partner_vals, order_vals,
                      order_ids, ProductObj, OrderObj):
        """Method import_orders to import the orders from magento to odoo"""
        for item in items:
            if str(item['increment_id']) not in order_ids:
                # This is a new order check the customer associated with the
                # order, if the customer is new, then create a new customer,
                # otherwise select existing record
                customer_id = self.find_customer_id(item, partner_ids,
                                                    partner_vals,
                                                    main=False)
                if item['customer_is_guest'] == 0:
                    partner_ids.append(str(item['customer_id']) if item['customer_id'] not in partner_ids else None)
                order_vals['magento'] = True
                order_vals['magento_id'] = str(item['increment_id'])
                order_vals['partner_id'] = customer_id
                order_vals['magento_status'] = (item.get('state') or
                                                item.get('status'))
                order_vals['date_order'] = item.get('created_at')
                order_line = []
                prod_rec = []
                for line in item['items']:
                    try:
                        custom_list = line['sku'].rsplit("-", len(
                            line['product_option']['extension_attributes']['custom_options']))
                    except:
                        custom_list = line['sku'].rsplit("-", 0)
                    for val in custom_list:
                        tax_name = (self.env['account.tax'].search(
                            [('amount', '=', line['tax_percent']),
                             ('magento', '=', True)])).ids if 'tax_percent' in line else []
                        if line['price'] != 0:
                            prod_rec = ProductObj.search([('default_code', '=', val)], limit=1)
                        if not prod_rec:
                            continue
                        temp = {
                            'product_id': prod_rec.id,
                            'product_uom_qty': line['qty_ordered'],
                            'price_unit': line['price'] if line['price'] else 0,
                            'tax_id': [(6, 0, tax_name)],
                        }
                        order_line.append((0, 0, temp))
                    order_vals['order_line'] = order_line
                ship_product_id = []
                if item['shipping_amount']:
                    template_search = self.env['product.template'].search([('name', '=', 'Shipping Charge'), ('type', '=', 'service')])
                    ship_tax = self.env['account.tax'].search([('amount', '=', item['shipping_tax_amount']),('magento', '=', True)]).ids
                    ProductAccount = template_search._get_product_accounts()
                    if template_search:
                        product_search = self.env['product.product'].search([('product_tmpl_id', '=', template_search.id)])
                        ship = {
                            'name': 'Shipping Charge',
                            'product_id': product_search.id,
                            'product_uom_qty': 1,
                            'price_unit': item['shipping_incl_tax'],
                            'tax_id': [(6, 0, ship_tax)],
                        }
                    else:
                        ship_product = self.env['product.product'].create({
                            'name': 'Shipping Charge',
                            'type': 'service'
                        })
                        ProductAccount = ship_product.product_tmpl_id._get_product_accounts()
                        ship = {
                            'name': ship_product.name,
                            'product_id': ship_product.id,
                            'product_uom_qty': 1,
                            'price_unit': item['shipping_incl_tax'],
                            'tax_id': [(6, 0, ship_tax)],
                        }
                    order_line.append((0, 0, ship))
                    ship_product_id.append(ship['product_id'])
                order_vals['order_line'] = order_line
                if 'message_follower_ids' in order_vals:
                    order_vals.pop('message_follower_ids')
                order_vals['name'] = self.env['ir.sequence'].next_by_code('sale.order')
                order_id = OrderObj.create(order_vals)
                order_id.action_confirm()
                if order_id:
                    self._create_invoice_magento(order_id)
                else:
                    _logger.info("Unable to create order")

    def _create_invoice_magento(self, order_id):
        """Method create_invoice_magento to create an invoice in magento"""
        url = '/rest/V1/invoices?searchCriteria[filter_groups][0][filters][0][' \
              'field]=increment_id&searchCriteria[filter_groups][0][filters][0][' \
              'condition_type]=eq"&searchCriteria[filter_groups][0][filters][0][value]={id} '
        type = 'GET'
        config_url = url.replace('{id}', str(order_id.magento_id))
        check_invoice = self.env['magento.connector'].magento_api_call(
            headers={},
            url=config_url,
            type=type)
        if check_invoice.get('items'):
            inv_id = order_id._create_invoices()
            inv = self.env['account.move'].search([('id', '=', inv_id.id)])
            inv.update({'magento': True, })
            inv.action_post()

    def export_orders(self):
        """Method to import Customers from odoo to magento"""
        url = 'rest/V1/orders/'
        request_type = 'POST'
        headers = {
            'Content-Type': 'application/json'
        }
        orders_data = self.get_orders_data()
        if not orders_data:
            return
        split_data = [orders_data[i:i + 5] for i in
                      range(0, len(orders_data), 10)]
        for data in split_data:
            delay = self.with_delay(priority=1, eta=5)
            delay.magento_import_orders(order_data=data, url=url,
                                        headers=headers, type=request_type)

    def get_orders_data(self):
        """Method get_customer_data to get the customer data to export to
        magento"""
        catalog_data = []
        sale_orders = self.env['sale.order'].search([('magento', '=', False)])
        if sale_orders:
            for order in sale_orders:
                lines = []
                split_name = order.partner_id.name.split(' ')
                first_name = split_name[0]
                last_name = split_name[1] if len(split_name) > 1 else ' '
                for line in order.order_line:
                    order_line = {
                        "sku": line.product_id.default_code,
                        "name": line.product_id.name,
                        "qty_ordered": line.product_uom_qty,
                        "original_price": line.price_unit,
                        "price": line.price_unit,
                        "tax_amount": line.price_tax,
                        "tax_percent": line.tax_id.amount,
                        "discount_amount": line.discount,
                        "row_total": line.product_uom_qty * line.price_unit,
                    }
                    lines.append(order_line)
                address = {
                    "country_id": "US",
                    "street": [order.partner_id.street,
                               order.partner_id.street2],
                    "postcode": order.partner_id.zip,
                    "city": order.partner_id.city,
                    "firstname": first_name,
                    "lastname": last_name,
                    "email": order.partner_id.email if order.partner_id.email else f"{first_name.lower()}@gmail.com",
                    "telephone": order.partner_id.phone
                }
                order_list = []
                order_data = {
                    "entity": {
                        "customer_id": order.partner_id.magento_id,
                        "customer_firstname": first_name,
                        "customer_lastname": last_name if last_name else ' ',
                        "store_id": 1,
                        "customer_email": order.partner_id.email if order.partner_id.email else f"{first_name.lower()}@gmail.com",
                        "payment": {
                            "method": "checkmo"
                        },
                        "status": "processing" if order.invoice_ids else "pending",
                        "customer_is_guest": 0,
                        "extension_attributes": {
                            "shipping_assignments": [{
                                "shipping": {
                                    "address": address,
                                    "method": "flatrate_flatrate"
                                }
                            }]
                        },
                        "billing_address": address,
                        "items": lines,
                        "subtotal": order.tax_totals['amount_untaxed'],
                        "grand_total": order.tax_totals['amount_total'],
                        "tax_amount": order.tax_totals['groups_by_subtotal'][
                            'Untaxed Amount'][0]['tax_group_amount'] if
                        order.tax_totals['groups_by_subtotal'][
                            'Untaxed Amount'] else 0,
                        "total_due": order.amount_total,
                    }
                }
                order_list.append(order_data)
                order_list.append(order)
                catalog_data.append(order_list)
            return catalog_data or None

    def magento_import_orders(self, order_data, url, headers, type):
        """To import customer to magento from odoo"""
        for data in order_data:
            try:
                order_list = self.env['magento.connector'].magento_api_call(
                    headers=headers,
                    url=url,
                    type=type,
                    data=data[0]
                )
                if order_list.get('entity_id'):
                    data[1].write({
                        'magento': True,
                        'magento_id': order_list.get('increment_id')
                    })
            except Exception as e:
                pass
            _logger.info(f"{data[1].name} Customer updated in Magento")
