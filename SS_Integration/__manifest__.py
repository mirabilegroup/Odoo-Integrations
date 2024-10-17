{
    'name': 'S&S Vendor API Integration',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Sync products and inventory from vendor API',
    'description': """
        Syncs products, categories, and inventory from a vendor's API.
    """,
    'depends': ['base', 'product', 'stock'],
    'data': [
        'data/cron_jobs.xml',  # Add this line to include the cron job
    ],
    'installable': True,
    'application': True,
}
