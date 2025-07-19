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
        'views/stock_move_line_detailed_operation_tree_dimension.xml',
        'views/stock_move_line_form_dimensions.xml',
        'views/production_lot_tree_dimensions.xml',
        'views/stock_quant_tree_dimensions.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
