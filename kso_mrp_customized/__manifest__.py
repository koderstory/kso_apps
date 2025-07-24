# -*- coding: utf-8 -*-
{
    'name': 'Hide Produce Button by State',
    'version': '1.0.0',
    'summary': 'Hide the Produce button except when MO is in progress',
    'category': 'Manufacturing',
    'author': 'Your Company',
    'website': 'https://your.company',
    'license': 'LGPL-3',
    'depends': ['mrp'],
    'data': [
        'views/mrp_hide_produce_all.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}