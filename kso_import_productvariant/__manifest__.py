{
    'name': 'KSO: Import Product - Variant',
    'version': '18.0.0.0',
    'category': 'Product',
    'summary': """Import product data - its variant -""",
    'description': """
        
    """,
    'author': 'Koderstory',
    'company': 'Koderstory',
    'maintainer': 'Koderstory',
    'website': 'https://koderstory.com',
    'depends': ['base', 'stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/import_product_variant.xml',
    ],
    # 'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': True,
    'application': False,
}
