{
    'name': 'kso_product_approval',
    'summary': "Enforce product approval with a sourcing step before final approval.",
    'version': '18.0.0.0.1',
    'category': 'Product',
    'website': 'http://www.koderstory.com/',
    'description': """
Adds a three-stage workflow (Draft → Sourcing → Approved) for products.
Only members of “Product Sourcing” can move Draft→Sourcing, and only “Product Manager” can move Sourcing→Approved.
""",
    'author': 'koderstory',
    'maintainer': 'koderstory',
    'support': 'hello@koderstory.com',
    'license': 'LGPL-3',
    'depends': ['sale_management', 'purchase', 'stock'],
    'data': [
        'groups.xml',
        'views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': True,
}
