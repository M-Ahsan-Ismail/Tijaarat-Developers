from odoo import api, fields, models, _, exceptions
from datetime import datetime,timedelta
from odoo.tools import format_datetime
from odoo.exceptions import UserError, ValidationError


class HR_Leave_Type_Inherit(models.Model):
    _inherit = 'hr.leave.type'

    exclude_weekend = fields.Boolean(string="Exclude Weekend",copy=False)

    #Karimdad Start
    max_allowed = fields.Integer(string="Annual Allowed Leaves")
    #Karimdad End
    
    #Mudasir Start
    is_annual=fields.Boolean(string="Is Annual",default=False)
    is_casual=fields.Boolean(string="Is Casual",default=False)
    is_sick=fields.Boolean(string="Is Sick",default=False)
    is_unpaid=fields.Boolean(string="Is unpaid",default=False)
    #Mudasir End

class Time_Off_Inherit(models.Model):
    _inherit='hr.leave'

    #inherit the function in order to remove weekend
    @api.depends('number_of_days','request_date_from', 'request_date_to', 'holiday_status_id.exclude_weekend')
    def _compute_number_of_days_display(self):
        for rec in self:
            if rec.holiday_status_id.exclude_weekend and rec.request_date_from and rec.request_date_to:
                start_date = rec.request_date_from
                end_date = rec.request_date_to
                num_days = 0
                current_date = start_date
                while current_date <= end_date:
                    if current_date.weekday() < 5:  # Monday to Friday are 0-4
                        num_days += 1
                    current_date += timedelta(days=1)
                rec.number_of_days = num_days
                rec.number_of_days_display = num_days
                self._compute_display_name()
            else:
                rec.number_of_days = (rec.request_date_to - rec.request_date_from).days + 1 if rec.request_date_from and rec.request_date_to else 0
                rec.number_of_days_display = rec.number_of_days