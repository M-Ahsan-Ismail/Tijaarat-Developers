# -*- coding: utf-8 -*-
{
    'name': "gd_custom_reports",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "M.Rizwan",
    'website': "https://www.hcc-me.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'account_accountant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/report.xml',
        # 'report/jv_document_view.xml',
        'report/bank_cash_voucher_template.xml',
        'report/bill_invoice_report_inherit_view.xml',
        # 'report/gd_custom_headerfotter.xml',
        # 'views/po_reqQuotation_report_doc.xml',
        # 'views/po_report_inherited_doc.xml',
        # 'views/invoice_document_inherited.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}

