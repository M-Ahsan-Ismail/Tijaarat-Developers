# -*- coding: utf-8 -*-
{
    'name': "Account_custom_reports",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "M.Ahsan",


   
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'account_accountant'],

    # always loaded
    'data': [
        'report/bill_invoice_report_inherit_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}

