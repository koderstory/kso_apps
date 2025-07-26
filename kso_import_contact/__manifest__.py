{
    'name': 'Contact Import from Excel',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Import Contacts from Excel File',
    'depends': ['base', 'contacts','stock',],
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'views/contact_import.xml',
    ],
    'installable': True,
}
