# -*- coding: utf-8 -*-
{
    'name': "tijaarat_inventory_custom",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "M.Rizwan",
    'website': "https://bssuniversal.com/",
    'version': '17.0.1.0',
    "license": "LGPL-3",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'analytic', 'account', 'project', 'account_accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/quality_check_wizard_view.xml',
        'views/stock_picking_inherited_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
