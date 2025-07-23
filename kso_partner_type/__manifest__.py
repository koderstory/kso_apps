# partner_flags/__manifest__.py
{
    "name": "Partner Customer/Vendor Flags",
    "version": "18.0.1.0.0",
    "summary": "Add Customer and Vendor check-boxes to partners",
    "category": "Custom",
    "author": "Your Name",
    "depends": ["base", "account", 'purchase'],
    "data": [
        "views/res_partner_type.xml",
        # "views/res_partner_kanban_customer_filter.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
    'auto_install': True,
}
