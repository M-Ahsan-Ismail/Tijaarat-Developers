{
    'name': 'subcontractor_bill',  # Module name
    'author': 'Business Solutions & Services',  # Author name
    'maintainer': 'M.Ahsan',
    'category': 'BSS',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'project', 'stock'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'data': [
        'security/ir.model.access.csv',
        'report/sub_contractor_report_view.xml',
        'views/menuitems.xml',
        'views/sub_contractor_bill_view.xml',
    ],

    'images': ['static/description/icon.png'],
}
