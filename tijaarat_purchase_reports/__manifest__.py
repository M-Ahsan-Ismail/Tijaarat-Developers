# -*- coding: utf-8 -*-


{
    'name': "Purchase Order PFD Report Inherit",

    'summary': "Tijaarat Purchase Order PFD Report",

    'description': """
Long description of module's purpose
    """,

    'author': "M.Ahsan",
    'website': "https://bssuniversal.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase','purchase_requisition'],

    # always loaded
    'data': [
        'report/report.xml',
        'report/tijaarat_purchase_report_template.xml',
        'report/tijaarat_reports_comparison.xml',
        'views/tijaarat_purchase_order_custom_view.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
