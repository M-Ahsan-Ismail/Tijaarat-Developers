# -*- coding: utf-8 -*-


{
    'name': "Purchase Order PFD Report Inherit",

    'summary': "Tijaarat Purchase Order PFD Report",

    'description': """
Long description of module's purpose
    """,

    'author': "M.Rizwan & M.Ahsan",
    'website': "https://bssuniversal.com/",

    # for the full list
    'category': 'Customizations',
    'version': '17.0.1.0',
    "license": "LGPL-3",

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'purchase_requisition', 'material_purchase_requisitions','tijaarat_po_approval_workflow'],

    # always loaded
    'data': [
        'report/tijaarat_purchase_report_template.xml',
        'report/comparision_report.xml',
        'views/tijaarat_purchase_order_custom_view.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
