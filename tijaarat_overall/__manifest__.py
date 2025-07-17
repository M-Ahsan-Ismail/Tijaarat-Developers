{
    'name': 'tijaarat_overall',  # Module name
    'author': 'Business Solutions & Services',  # Author name
    'maintainer': 'M.Ahsan & M.Rizwan',
    'category': 'BSS',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'stock', 'purchase_stock','account','account_accountant'],  # Dependencies
    'installable': True,
    'application': True,
    'version': '17.0.1.0',
    "license": "LGPL-3",
    'data': [
        # 'security/ir.model.access.csv',
        'report/bill_invoice_report_inherit_view.xml',
        'report/stock_picking_report_inherit_view.xml',
        'views/po_overall.xml',

    ],

}
