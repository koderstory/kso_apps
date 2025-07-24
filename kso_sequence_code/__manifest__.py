# -*- coding: utf-8 -*-
{
    "name": "KSO Document Sequences",
    "version": "1.0",
    "summary": "Override PO/MO and add IT/DO sequences",
    "category": "Custom",
    "author": "Your Name or Company",
    "depends": [
        "purchase",
        "mrp",
        "stock",
    ],
    "data": [
        "data/ir_sequence_data.xml",
    ],
    "post_init_hook": "post_init_sequences",
    "installable": True,
    "application": False,
    "auto_install": True,
}
