{
    'name': 'tijaarat_maintenance_custom',  # Module name
    'author': "M.Rizwan",
    'website': "https://bssuniversal.com/",
    'description': "Tijaarat Maintenance Development",  # Description about the app
    'version': '17.0.1.0',  # Correct version format for Odoo 17
    'summary': 'Custom',  # Brief info about the app
    'sequence': 2,  # Position in the apps menu
    'category': 'Business',  # Category displayed in info
    "license": "LGPL-3",
    'depends': ['base', 'maintenance', 'account', 'account_accountant'],  # Dependencies
    'installable': True,
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/maintenance_data.xml',
        'views/tijaarat_maintenance_custom_view.xml',
        'wizard/maintenance_approval_wizard_view.xml',
    ],

}
