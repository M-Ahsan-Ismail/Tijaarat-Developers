# -*- coding: utf-8 -*-
{
    'name': "tijaarat_fund_requisition",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "M.Rizwan",
    'website': "https://www.bssuniversal.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.1.0',
    "license": "LGPL-3",

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'account', 'account_accountant', 'analytic', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/fund_requisition_view.xml',
        'report/report.xml',
        'report/fund_requisition_report_temp_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
