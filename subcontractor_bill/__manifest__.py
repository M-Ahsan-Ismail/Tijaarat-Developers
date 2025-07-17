{
    'name': 'subcontractor_bill',  # Module name
    'author': 'Business Solutions & Services',  # Author name
    'maintainer': 'M.Ahsan',
    'category': 'BSS',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'project', 'stock', 'odoo_job_costing_management','account','account_accountant'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'data': [
        'security/ir.model.access.csv',
        'report/sub_contractor_report_view.xml',
        'data/ir_sequence_record.xml',
        'views/menuitems.xml',
        'views/sub_contractor_bill_view.xml',
        'views/res_partner_inherit_view.xml',
        'views/account_move_inherit_view.xml',
        'views/res_config_account_settings_inherited_view.xml',
    ],

    'images': ['static/description/icon.png'],
}
