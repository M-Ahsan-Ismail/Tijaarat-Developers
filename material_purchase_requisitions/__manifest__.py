# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Requisitions Material Stock and Purchase by Employees',
    'version': '10.7.8',
    'price': 79.0,
    'currency': 'EUR',
    "license": "LGPL-3",
    'summary': """Product / Material Purchase Requisition and Stock Request by User""",
    'description': """
    Material Purchase Requisitions
    This module allowed Purchase requisition of employee.
Purchase_Requisition_Via_iProcurement
Purchase Requisitions
Purchase Requisition
iProcurement
Inter-Organization Shipping Network
Online Requisitions
Issue Enforcement
Inventory Replenishment Requisitions
Replenishment Requisitions
MRP Generated Requisitions
generated Requisitions
purchase Sales Orders
Complete Requisitions Status Visibility
Using purchase Requisitions
purchase requisitions
replenishment requisitions
employee Requisition
employee purchase Requisition
user Requisition
stock Requisition
inventory Requisition
warehouse Requisition
factory Requisition
department Requisition
manager Requisition
Submit requisition
Create purchase Orders
purchase Orders
product Requisition
item Requisition
material Requisition
product Requisitions
material purchase Requisition
material Requisition purchase
purchase material Requisition
product purchase Requisition
item Requisitions
material Requisitions
products Requisitions
purchase Requisition Process
Approving or Denying the purchase Requisition
Denying purchase Requisition​
construction management
real estate management
construction app
Requisition
Requisitions
indent management
indent
indent stock
indent system
indent request
indent order
odoo indent
internal Requisitions
* INHERIT hr.department.form.view (form)
* INHERIT hr.employee.form.view (form)
* INHERIT stock.picking.form.view (form)
purchase.requisition search (search)
purchase.requisition.form.view (form)
purchase.requisition.view.tree (tree)
purchase_requisition (qweb)
Main Features:
allow your employees to Create Purchase Requisition.
Employees can request multiple material/items on single purchase Requisition request.
Approval of Department Head.
Approval of Purchase Requisition Head.
Email notifications to Department Manager, Requisition Manager for approval.
- Request for Purchase Requisition will go to stock/warehouse as internal picking / internal order and purchase order.
- Warehouse can dispatch material to employee location and if material not present then procurment will created by Odoo standard.
- Purchase Requisition user can decide whether product requested by employee will come from stock/warehouse directly or it needs to be purchase from vendor. So we have field on requisition lines where responsible can select Requisition action: 1. Purchase Order 2. Internal Picking. If option 1 is selected then system will create internal order / internal picking request and if option 2 is selected system will create multiple purchase order / RFQ to vendors selected on lines.
- For more details please see Video on live preview or ask us by email...


    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpeg'],
    #'live_test_url': 'https://youtu.be/1AgKs7gfe4M',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/material_purchase_requisitions/304',#'https://youtu.be/byR2cM0c274',
    'category': 'Inventory/Inventory',
    'depends': [
                'stock',
                'hr',
                'purchase',
                ],
    'data':[
        'security/security.xml',
        'security/multi_company_security.xml',
        'security/ir.model.access.csv',
        'data/purchase_requisition_sequence.xml',
        'data/employee_purchase_approval_template.xml',
        'data/confirm_template_material_purchase.xml',
        'report/purchase_requisition_report.xml',
        'views/purchase_requisition_view.xml',
        # 'views/hr_employee_view.xml',
        'views/hr_department_view.xml',
        'views/stock_picking_view.xml',
        'views/purchase_order_line_view.xml',
        'report/comparision_report_mpr.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
