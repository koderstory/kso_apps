{
    'name': 'BoM Import from Excel',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Import BoM from Excel File',
    'depends': ['base', 'mrp'],
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'views/bom_import.xml',
    ],
    'installable': True,
}
