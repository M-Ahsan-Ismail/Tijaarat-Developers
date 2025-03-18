{
    "name": "goods_receiving_report",
    "author": "Ahsan",
    "category": "Inventory/Purchase",
    "version": "17.0.1.0",
    "depends": ['purchase', 'stock', 'sale', 'sale_stock','material_purchase_requisitions',
                ],
    "data": [
        'security/ir.model.access.csv',
        'views/stock_move_lines_inherited.xml',
        'views/goods_receipt_report.xml',
        'views/stock_transfer_report.xml',
        'views/store_purchase_requisition_report.xml',
    ],

    "application": True,
    "auto_install": False,
    "installable": True,

}
