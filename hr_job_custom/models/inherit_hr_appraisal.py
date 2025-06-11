# from typing_extensions import ReadOnly
from email.policy import default
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class inheritHrAppraisal(models.Model):
    _inherit = 'hr.appraisal'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('new', 'To Confirm'),
        ('pending', 'Confirmed'),
        ('pending', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], default='new')

    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_for_approval', 'Submit For Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')],
        string="Approval Status",
        default='draft',
        readonly=True)
    request_ids = fields.One2many('approval.request', 'appraisal_id', string='Request')

    manager_rating = fields.Selection([
        ('partialAchieved', 'Partially Achieved'),
        ('developmentNeedsIdentified', 'Development Needs Identified'),
        ('achievedExpectations', 'Achieved Expectations'),
        ('exceededExpectations', 'Exceeded Expectations'),
        ('continuouslyExceededExpectations', 'Continuously Exceeded Expectations')
    ], string="Managers Rating")

    avg_manager_rating = fields.Float('Average Manager Rating', store=True, compute="_compute_avg_rating",
                                      default='0.0',
                                      help="This is the average of all the ratings the Manager has given this employee for this appraisal")
    avg_employee_rating = fields.Float('Average Employee Rating', store=True, compute="_compute_avg_rating",
                                       default='0.0',
                                       help="This is the average of all the ratings the Employee has given themselves for this appraisal")

    # goals_in_appraisal = fields.Integer("Goals in Appraisal", compute="compute_goals_in_appraisal")

    # @api.depends('employee_id', 'date_close')
    # def compute_goals_in_appraisal(self):
    #     for record in self:
    #         goals = self.env['hr.appraisal.goal'].search_count([
    #             ('employee_id', '=', record.employee_id.id),
    #             ('start_date', '<=', record.date_close),
    #             ('deadline', '>=', record.date_close),
    #             ('progression', '!=', '100')
    #         ])
    #         record.goals_in_appraisal = goals

    def action_open_goals(self):
        self.ensure_one()
        domain = [('employee_id', '=', self.employee_id.id), ('start_date', '<=', self.date_close),
                  ('deadline', '>=', self.date_close), ('progression', '!=', '100')]

        return {
            'name': _('%s Goals') % self.employee_id.name,
            'view_mode': 'kanban,tree,form,graph',
            'res_model': 'hr.appraisal.goal',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': domain,
            'context': {'default_employee_id': self.employee_id.id},
        }

    def _compute_avg_rating(self):
        avg_employee_rating = 0.0
        avg_manager_rating = 0.0

        # only traverse those goals that fall within the current appraisal period.
        # self.env.cr.commit()
        for record in self:
            # employee_goals = self.env['hr.appraisal.goal'].search(
            #     [('employee_id', '=', record.employee_id.id),
            #      ('state', '=', 'approved'),
            #      ('start_date', '>=', fields.Date.today().replace(month=1, day=1)),
            #      ('deadline', '<=', fields.Date.today().replace(month=12, day=31))],
            #     order='create_date desc'
            # )
            #
            # total_manager_rating = sum(float(goal.manager_rating) for goal in employee_goals)
            # total_employee_rating = sum(float(goal.employee_rating) for goal in employee_goals)
            # record.avg_manager_rating = total_manager_rating / len(employee_goals) if employee_goals else 0.0
            # record.avg_employee_rating = total_employee_rating / len(employee_goals) if employee_goals else 0.0
            record.avg_manager_rating = 0.0
            record.avg_employee_rating = 0.0
            # raise UserError(str([record.avg_employee_rating]))

    def submit_for_approval(self):
        approval_id = self.env['approval.category'].search([('name', '=', 'Appraisal Approvals')], limit=1)
        admin = self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_erp_manager').id)], limit=1)
        approvers = [(0, 0, {'user_id': admin.id})]

        if not approval_id:
            approval_id = self.env['approval.category'].create({
                'name': 'Appraisal Approvals',
                'manager_approval': 'approver',
                'description': 'Appraisal Approval requests',
                'approver_ids': approvers,
            })

        request = self.env['approval.request'].create({
            'name': self.employee_id.name,
            'request_owner_id': self.env.uid,
            'category_id': approval_id.id,
            'appraisal_id': self.id,
            'request_type': 'AppraisalRequest'

        })
        self.request_ids = [(4, request.id, 0)]
        request.action_confirm()
        self.approval_state = "submit_for_approval"

    def action_withdraw(self):
        request_id = self.env['approval.request'].search(
            [('appraisal_id', '=', self.id), ('request_status', '=', 'pending')])
        request_id.action_cancel()
        self.approval_state = 'draft'

    def open_related_approval(self):
        return {
            'name': 'Related Approval',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.request',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('appraisal_id', '=', self.id)]
        }

    @api.onchange('employee_id', 'manager_ids', 'employee_feedback_ids', 'date_close', 'manager_rating',
                  'department_id', 'rating', 'assessment_note', 'manager_feedback', 'note', 'skill_ids')
    def ristrict_at_submitted(self):
        if self.approval_state == 'submit_for_approval':
            raise UserError("Request is submitted for approval cannot change until approved")

    def action_done(self):
        if self.approval_state != "approved":
            raise UserError("Cant Mark Done until approved")
        else:
            super(inheritHrAppraisal, self).action_done()
