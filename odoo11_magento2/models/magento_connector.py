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
import json
from odoo import exceptions, models, _

logger = logging.getLogger(__name__)

try:
    import requests
except ImportError:
    logger.info(
        _("Unable to import requests, please install it with pip install "
          "requests"))


class MagentoConnector(models.Model):
    """Creates the model magento.connector"""
    _name = 'magento.connector'
    _description = 'Magento Connector'

    def magento_api_call(self, **kwargs):
        """
        We will be running the api calls from here
        :param kwargs: dictionary with all the necessary parameters,
        such as url, header, data,request type, etc
        :return: response obtained for the api call
        """
        if not kwargs:
            # no arguments passed
            raise ValueError("No arguments passed to magento_api_call")
        ICPSudo = self.env['ir.config_parameter'].sudo()
        # fetching access token from settings
        try:
            access_token = ICPSudo.get_param('odoo11_magento2.access_token')
        except Exception:
            access_token = False
        # fetching host name
        try:
            magento_host = ICPSudo.get_param('odoo11_magento2.magento_host')
        except Exception:
            magento_host = False
        if not access_token or not magento_host:
            raise exceptions.UserError(
                _('Please check the magento configurations!'))
        request_type = kwargs.get('type') or 'GET'
        complete_url = 'http://' + magento_host + kwargs.get('url')
        logger.info("%s", complete_url)
        headers = kwargs.get('headers')
        headers['Authorization'] = 'Bearer ' + access_token
        data = json.dumps(kwargs.get('data')) if kwargs.get('data') else None
        try:
            res = requests.request(request_type, complete_url, headers=headers,
                                   data=data, timeout=10)
            items = json.loads(res.text)
            return items
        except Exception as e:
            logger.info(_("Exception occured %s"), e)
            raise exceptions.UserError(_("Error Occured 5 %s") % e)
