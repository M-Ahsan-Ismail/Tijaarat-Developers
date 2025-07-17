# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = "project.project"

    #@api.multi
    def action_open_job_orders(self):
        # action = self.env.ref(
        #     "odoo_job_costing_management.action_view_job_orders"
        # )
        # action_read = action.read([])[0]
        self.ensure_one()
        action_read = self.env['ir.actions.act_window']._for_xml_id('odoo_job_costing_management.action_view_job_orders')
        action_read['domain']= [
            ('project_id', '=', self.id)
        ]
        action_read['context'] = {'default_project_id': self.id}
        return action_read

    #@api.multi
    def action_open_cost_sheet(self):
        # action = self.env.ref(
        #     "odoo_job_costing_management.action_job_costing"
        # )
        # action_read = action.read([])[0]
        self.ensure_one()
        action_read = self.env['ir.actions.act_window']._for_xml_id('odoo_job_costing_management.action_job_costing')
        action_read['domain']= [
            ('project_id', '=', self.id)
        ]
        action_read['context'] = {'default_project_id': self.id}
        return action_read

    #@api.multi
    def action_open_sheet_materials(self):
        # action = self.env.ref(
        #     "job_costing_dashboard.action_material_cost_sheet_line"
        # )
        # action_read = action.read([])[0]

        self.ensure_one()
        action_read = self.env['ir.actions.act_window']._for_xml_id('job_costing_dashboard.action_material_cost_sheet_line')
        action_read['domain']= [
            ('direct_id.project_id', '=', self.id),
            ('job_type', '=', 'material')
        ]
        return action_read

    #@api.multi
    def action_open_sheet_labours(self):
        # action = self.env.ref(
        #     "job_costing_dashboard.action_labour_cost_sheet_line"
        # )
        self.ensure_one()
        action_read = self.env['ir.actions.act_window']._for_xml_id('job_costing_dashboard.action_labour_cost_sheet_line')
        # action_read = action.read([])[0]
        action_read['domain'] = [
            ('direct_id.project_id', '=', self.id),
            ('job_type', '=', 'labour')
        ]
        return action_read

    #@api.multi
    def action_open_sheet_overheads(self):
        # action = self.env.ref(
        #     "job_costing_dashboard.action_overhead_cost_sheet_line"
        # )
        self.ensure_one()
        action_read = self.env['ir.actions.act_window']._for_xml_id('job_costing_dashboard.action_overhead_cost_sheet_line')
        # action_read = action.read([])[0]
        action_read['domain']= [
            ('direct_id.project_id', '=', self.id),
            ('job_type', '=', 'overhead')
        ]
        return action_read

    # New Job Cost Sheets
    def action_create_cost_sheet(self):
        context = self.env.context.copy()
        context.update({'default_project_id': self.id})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'job.costing',
            'view_mode': 'form',
            'res_id': False,
            'target': 'current',
            'context': context,
            'flags': {
                'form': {
                    'action_buttons': True,
                    'options': {
                        'mode': 'create'
                    }
                }
            }
        }

    # New Job Order
    def action_create_job_order(self):
        context = self.env.context.copy()
        context.update({'default_project_id': self.id})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'form',
            'res_id': False,
            'target': 'current',
            'context': context,
            'flags': {
                'form': {
                    'action_buttons': True,
                    'options': {
                        'mode': 'create'
                    }
                }
            }
        }

    # Job Order PO
    #@api.multi
    def action_open_job_orders_po(self):
        self.ensure_one()
        purchase_order_lines_obj = self.env['purchase.order.line']
        # line_ids = purchase_order_lines_obj.search([('account_analytic_id','=', self.analytic_account_id.id)]).ids
        # line_ids = purchase_order_lines_obj.search([('analytic_distribution_stored_char', '=ilike', f'%"{self.analytic_account_id.id}":%')])
        line_ids = purchase_order_lines_obj.search([('analytic_distribution', '=', {str(self.analytic_account_id.id): 100})])
        #action = self.env.ref('purchase.purchase_form_action').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_form_action')
        action['domain'] = [('order_line','in', line_ids.ids)]
        return action

    # Job Order HR Timesheet
    #@api.multi
    def action_open_job_orders_hr_timesheet(self):
        self.ensure_one()
        #action = self.env.ref('hr_timesheet.act_hr_timesheet_line').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('hr_timesheet.act_hr_timesheet_line')
        action['domain'] = [('project_id','=', self.id)]
        return action

    # Job Order Vendor Invoice
    #@api.multi
    def action_open_job_orders_vendor_invoice(self):
        self.ensure_one()
#        account_invoice_lines_obj = self.env['account.invoice.line']
        account_invoice_lines_obj = self.env['account.move.line']
#        line_ids = account_invoice_lines_obj.search([('account_analytic_id','=', self.analytic_account_id.id)]).ids
        # line_ids = account_invoice_lines_obj.search([('analytic_distribution_stored_char', '=ilike', f'%"{self.analytic_account_id.id}":%')])
        # analytic_distribution = {str(self.analytic_account_id.id): 100}
        line_ids = account_invoice_lines_obj.search([('analytic_distribution', '=', {str(self.analytic_account_id.id): 100})])
#        action = self.env.ref('account.action_invoice_tree2').sudo().read()[0]
        #action = self.env.ref('account.action_move_out_invoice_type').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        action['domain'] = [('id','in', line_ids.mapped('move_id').ids),('move_type', '=', 'in_invoice')]
        return action

    # All Job Order, Project, Task Document Open
    #@api.multi
    def action_open_document(self):
        # action = self.env.ref(
        #     "base.action_attachment"
        # )
        self.ensure_one()
        action_read = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        # action_read = action.read([])[0]
        action_read['domain']= [
            ('res_model', 'in', ['project.project', 'project.tsak','job.costing'])
        ]
        return action_read

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
