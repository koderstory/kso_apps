{
    'name': 'Sales Order Process Customized',
    'version': '1.0',
    'category': 'Sales',
    'depends': ['sale_management', 'kso_partner_code',],
    'data': [
        'security/sale_order_group.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
