{
    'name': 'Lot Dimensions',
    'version': '1.0',
    'summary': 'Add length/width/height to lot/serial records',
    'category': 'Inventory',
    'author': 'Your Name',
    'depends': ['stock'],
    'data': [
        'views/stock_lot_views.xml',
        'views/stock_move_line_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
