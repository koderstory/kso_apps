{
    'name': 'Partner Is Customer Vendor Fields',
    'version': '18.0.1.0.0',
    'author': 'Your Name',
    'category': 'Contacts',
    'summary': 'Add boolean fields is_customer and is_vendor to partners',
    'depends': ['base', 'contacts', 'purchase', 'sale_management'],
    'data': [
        'views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
}