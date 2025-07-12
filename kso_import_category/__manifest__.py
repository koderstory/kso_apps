{
    'name': 'KSO: Import Product Category',
    'version': '18.0.1.0.0',
    'category': 'Product',
    'summary': """Import product categories using a slash-separated path.""",
    'description': """
        This module adds a wizard to import product categories from a CSV file.
        The CSV should include a column 'category_path' containing paths like:
            material
            material / supporting
            material / supporting / skrew
        The wizard will create or update the category hierarchy accordingly.
    """,
    'author': 'Koderstory',
    'company': 'Koderstory',
    'maintainer': 'Koderstory',
    'website': 'https://koderstory.com',
    'depends': ['product', 'stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/category_import_wizard_view.xml',
    ],
    # 'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': True,
    'application': True,
}
