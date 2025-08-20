# -*- coding: utf-8 -*-
{
    'name': 'KSO: MRP Customized',
    'version': '1.0.0',
    'summary': 'Customized MRP',
    'category': 'Manufacturing',
    'author': 'Koderstory',
    'website': 'https://koderstory.com',
    'license': 'LGPL-3',
    'depends': ['mrp'],
    'data': [
        'views/mrp_hide_produce_all.xml',
        'views/mrp_wizard_check.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}