import requests
from odoo import models, fields, api

class VendorProductIntegration(models.Model):
    _name = 'vendor.product.integration'
    _description = 'Vendor API Product Integration'

    api_url = fields.Char(string="API URL", default="https://vendorapi.com/")
    api_key = fields.Char(string="API Key")  # Enter your API key here
    synced_products = fields.Integer(string="Synced Products", default=0)

    def _get_headers(self):
        """Prepare headers for API requests"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    @api.model
    def sync_categories(self):
        """Sync product categories from vendor API"""
        url = f"{self.api_url}categories"
        response = requests.get(url, headers=self._get_headers())

        if response.status_code == 200:
            categories = response.json()
            for category in categories:
                self.env['product.category'].create({
                    'name': category['name']
                })
        else:
            raise Exception(f"Error fetching categories: {response.content}")

    @api.model
    def sync_products(self):
        """Sync products and inventory from vendor API"""
        # Get products
        url = f"{self.api_url}products"
        response = requests.get(url, headers=self._get_headers())

        if response.status_code == 200:
            products = response.json()
            for product in products:
                existing_product = self.env['product.product'].search([('default_code', '=', product['sku'])])

                if not existing_product:
                    # Create product in Odoo
                    new_product = self.env['product.product'].create({
                        'name': product['name'],
                        'default_code': product['sku'],
                        'list_price': product['price'],
                        'type': 'product',  # Storable product
                        'categ_id': self.env['product.category'].search([('name', '=', product['category_name'])], limit=1).id
                    })
                else:
                    new_product = existing_product

                # Update inventory
                inventory_url = f"{self.api_url}inventory?sku={product['sku']}"
                inv_response = requests.get(inventory_url, headers=self._get_headers())
                if inv_response.status_code == 200:
                    stock_data = inv_response.json()
                    qty_available = stock_data.get('quantity_available', 0)

                    # Update stock in Odoo
                    new_product.qty_available = qty_available

                self.synced_products += 1
        else:
            raise Exception(f"Error fetching products: {response.content}")

    @api.model
    def sync_all(self):
        """Sync categories and products with inventory in one go"""
        self.sync_categories()
        self.sync_products()
