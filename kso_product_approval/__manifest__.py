{
    'name': 'kso_product_approval',
    'summary': "Multi-stage product + BoM confirmation all in one module",
    'version': '18.0.0.0.2',
    'category': 'Product',
    'website': 'http://www.koderstory.com/',
    'description': """
This module enforces:

  • Product workflow: Draft → Design → SCM → R&D → Approved  
  • BoM workflow: Draft → To Approve → Approved → Cancelled  

""",
    'author': 'koderstory',
    'maintainer': 'koderstory',
    'support': 'hello@koderstory.com',
    'license': 'LGPL-3',
    'depends': ['sale_management', 'mrp', 'purchase', 'stock'],
    'data': [
        'security/groups_product.xml',
        'security/groups_bom.xml',
        # 'security/ir.model.access.csv',
        'views/product.xml',
        'views/bom.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
