from odoo import api, fields, models, _
import calendar
# from datetime import datetime, time, timedelta
import datetime
import math
# import datetime
import pytz
from odoo.tools import format_datetime
from odoo.tools import float_compare, format_date
from odoo.exceptions import AccessDenied, UserError


import logging
_logger = logging.getLogger(__name__)


class EmployeeExt(models.Model):
    _inherit = 'hr.employee'

    lates_this_month = fields.Integer(string="Late days this Month", compute="_check_late_this_month")
    half_days_this_month = fields.Integer(string="Half days this Month", compute="_check_half_this_month")
    flag_for_late = fields.Boolean(string="Flag for Lates", default=True)
    flag_for_half = fields.Boolean(string="Flag for Half-Days", default=True)

    @api.onchange('no_of_late')
    def _check_late_this_month(self):
        for rec in self:
            current_month = datetime.datetime.now().month
            rec.lates_this_month = 0
            count = 0
            attendance = self.env['hr.attendance'].search([('employee_id', '=', rec.id)], order='check_in desc')
            # attendance=self.env['hr.attendance'].search([('employee_id','=',rec.id)])
            if attendance:
                for att in attendance:
                    att_check_in = att.check_in
                    att_check_in_month = att_check_in.month

                    if current_month - att_check_in_month == 1:
                        break

                    if att_check_in_month == current_month and att.status == 'late':
                        count += 1

            rec.lates_this_month = count

    @api.onchange('no_of_half')
    def _check_half_this_month(self):
        for rec in self:
            current_month = datetime.datetime.now().month
            rec.half_days_this_month = 0
            count = 0

            attendance = self.env['hr.attendance'].search([('employee_id', '=', rec.id)], order='check_in desc')

            if attendance:
                for att in attendance:
                    att_check_in = att.check_in

                    att_check_in_month = att_check_in.month
                    if (current_month - att_check_in_month) == 1:
                        break

                    if att_check_in_month == current_month and att.status == 'half_day':
                        count += 1

            rec.half_days_this_month = count

    # #this function must automatically create a request for time off
    # #the description for this would by the type of leave incurred by the late/half-day condition
    @api.onchange('lates_this_month', 'half_days_this_month')
    def _update_remaining_leaves(self):

        new_entry = {}

        for rec in self:
            taken_casual = taken_annual_jan_june = taken_annual_july_dec = 0
            remaining_casual = remaining_annual_jan_june = remaining_annual_july_dec = 0
            allocated_casual = allocated_annual_jan_june = allocated_annual_july_dec = 0

            morning_time_from = datetime.time(4, 0, 0)
            morning_time_to = datetime.time(13, 0, 0)

            evening_time_from = datetime.time(8, 0, 0)
            evening_time_to = datetime.time(17, 0, 0)

            casual_leave_id = 0
            annual_leave_jan_june_id = 0
            annual_leave_july_dec_id = 0
            unpaid_leave_id = 0
            holiday_type = ''

            current_month = datetime.datetime.now().month
            leaves_late_days = rec.lates_this_month // 4
            leaves_half_days = rec.half_days_this_month // 2

            leaves = self.env['hr.leave'].search([('employee_id', '=', rec.id), (
            'holiday_status_id', 'in', ['Casual Leave', 'Annual Leave Jul to Dec', 'Annual Leave Jan to June']),
                                                  ('state', 'in', ['validate', 'confirm'])])
            _logger.info("Leaves records: %s", leaves)
            # obtain allocations for current user
            allocations = self.env['hr.leave.allocation'].search([('employee_id', '=', rec.id), '|', (
            'holiday_status_id', 'in', ['Casual Leave', 'Annual Leave Jul to Dec', 'Annual Leave Jan to June']),
                                                                  ('state', '=', 'validate')])

            # latest attendance entry
            attendances = self.env['hr.attendance'].search([('employee_id', '=', rec.id)], order="check_in desc",
                                                           limit=1)

            for alloc in allocations:
                if alloc.holiday_status_id.is_casual:
                    casual_leave_id = alloc.holiday_status_id

                    holiday_type = alloc.holiday_type
                    temp = alloc.duration_display.split(' ')
                    allocated_casual += int(temp[0])

                if alloc.holiday_status_id.is_annual:
                    if 'Jan to June' in alloc.holiday_status_id.name:
                        annual_leave_jan_june_id = alloc.holiday_status_id
                        _logger.info('holiday_status_id: %s, annual_leave_jan_june_id: %s',
                                     alloc.holiday_status_id.name, annual_leave_jan_june_id)
                        temp = alloc.duration_display.split(' ')
                        allocated_annual_jan_june += int(temp[0])

                    if 'Jul to Dec' in alloc.holiday_status_id.name:
                        annual_leave_july_dec_id = alloc.holiday_status_id
                        _logger.info('holiday_status_id: %s, annual_leave_jul_dec_id: %s', alloc.holiday_status_id.name,
                                     annual_leave_july_dec_id)
                        temp = alloc.duration_display.split(' ')
                        allocated_annual_july_dec += int(temp[0])

            for sus in leaves:
                # raise UserError(str([annual_leave_jan_june_id.id,'\n',sus.holiday_status_id.id]))
                if sus.holiday_status_id.is_casual:
                    temp = sus.duration_display.split(' ')
                    # raise UserError(int(temp[0]))
                    taken_casual += int(temp[0])

                if sus.holiday_status_id.is_annual:
                    _logger.info('leaves: ', sus.read())

                    if annual_leave_jan_june_id == sus.holiday_status_id:
                        temp = sus.duration_display.split(' ')
                        taken_annual_jan_june += int(temp[0])
                        # raise UserError(["Test1",taken_annual_jan_june])

                    if annual_leave_july_dec_id == sus.holiday_status_id:
                        # raise UserError(str([sus.read]))
                        temp = sus.duration_display.split(' ')
                        taken_annual_july_dec += int(temp[0])
                        # raise UserError(["Test2",taken_annual_july_dec])

            remaining_casual = allocated_casual - taken_casual
            remaining_annual_jan_june = allocated_annual_jan_june - taken_annual_jan_june
            remaining_annual_july_dec = allocated_annual_july_dec - taken_annual_july_dec

            # raise UserError([str(leaves),remaining_annual_jan_june,remaining_annual_july_dec])

            if attendances:
                att_check_in = attendances.check_in
                att_check_in_date = att_check_in.date()
                att_check_in_month = att_check_in.month

                morning_leave_date_from = datetime.datetime.combine(att_check_in_date, morning_time_from)
                morning_leave_date_to = datetime.datetime.combine(att_check_in_date, morning_time_to)

                evening_leave_date_from = datetime.datetime.combine(att_check_in_date, morning_time_from)
                evening_leave_date_to = datetime.datetime.combine(att_check_in_date, morning_time_to)

                morning_date_from = fields.Datetime.to_string(morning_leave_date_from)
                morning_date_to = fields.Datetime.to_string(morning_leave_date_to)

                evening_date_from = fields.Datetime.to_string(evening_leave_date_from)
                evening_date_to = fields.Datetime.to_string(evening_leave_date_to)

                request_date_from = fields.Date.to_string(morning_leave_date_from.date())
                request_date_to = fields.Date.to_string(morning_leave_date_to.date())
                # a leave has been warranted and must be deducted
                new_entry = {
                    "holiday_allocation_id": False,
                    "state": "confirm",
                    "holiday_type": "employee",
                    "employee_id": attendances.employee_id.id,
                    "employee_ids": [
                        [
                            6,
                            False,
                            [
                                attendances.employee_id.id
                            ]
                        ]
                    ],
                    "mode_company_id": False,
                    "category_id": False,
                    "department_id": False,
                    "multi_employee": False,
                    "holiday_status_id": False,
                    "payslip_state": "normal",
                    # "date_from": "2024-02-28 03:00:00",
                    # "date_to": "2024-02-28 12:00:00",
                    "date_from": morning_date_from,
                    "date_to": morning_date_to,
                    "duration_display": "1 day",
                    "number_of_days": 1.0,
                    "request_date_from": request_date_from,
                    "request_date_from_period": "am",
                    "request_date_to": request_date_to,
                    "duration_display": "1 day",
                    "request_unit_half": False,
                    "request_unit_hours": False,
                    "request_hour_from": False,
                    "request_hour_to": False,
                    "name": False,
                    "supported_attachment_ids": [
                        [
                            6,
                            False,
                            []
                        ]

                    ]
                }

                # policy for lates
                if rec.lates_this_month > 0 and rec.lates_this_month % 4 == 0 and rec.flag_for_late == False:

                    # First deduct from Casual Leaves if avaialble
                    if remaining_casual > 0:
                        new_entry['holiday_status_id'] = casual_leave_id.id
                        new_entry['name'] = "4 Lates incurred"
                        # if not attendance.check_out and attendance.check_in.date()

                        _logger.info('late casual')
                        update_days = self.env['hr.leave'].create([new_entry])
                        update_days.number_of_days = math.ceil(update_days.number_of_days_display)
                        update_days.is_sys_generated = True
                        rec.flag_for_late = True
                        break

                    # Then deduct from Annual Leave if available
                    elif att_check_in_month in [1, 2, 3, 4, 5, 6] and remaining_annual_jan_june > 0:
                        new_entry['holiday_status_id'] = annual_leave_jan_june_id.id
                        new_entry['name'] = "4 Lates incurred"

                        # The newest half-day trigger comes over here and fails
                        # because annual leave cap for this half of the year is met
                        _logger.info('late annual1\n remaining annual Jan-June leaves: %s', remaining_annual_jan_june)
                        update_days = self.env['hr.leave'].create([new_entry])
                        update_days.number_of_days = math.ceil(update_days.number_of_days_display)
                        update_days.is_sys_generated = True
                        rec.flag_for_late = True
                        break

                    elif att_check_in_month in [7, 8, 9, 10, 11, 12] and remaining_annual_july_dec > 0:
                        new_entry['holiday_status_id'] = annual_leave_july_dec_id.id
                        new_entry['name'] = "4 Lates incurred"

                        _logger.info('late annual2')
                        update_days = self.env['hr.leave'].create([new_entry])
                        update_days.number_of_days = math.ceil(update_days.number_of_days_display)
                        update_days.is_sys_generated = True
                        rec.flag_for_late = True
                        break
                    # Otherwise count it as an Unpaid Leave
                    else:
                        # get id for 'Unpaid' leave type
                        unpaid_leave = self.env['hr.leave.type'].search([('is_unpaid', '=', True)])

                        new_entry['holiday_status_id'] = unpaid_leave.id
                        new_entry['name'] = "4 Lates incurred"

                        _logger.info('late unpaid')
                        update_days = self.env['hr.leave'].create([new_entry])
                        update_days.number_of_days = math.ceil(update_days.number_of_days_display)
                        update_days.is_sys_generated = True
                        rec.flag_for_late = True
                        break

                # check to ensure repeated requests for same leave incurment are avoided
                elif rec.lates_this_month % 4 != 0:
                    rec.flag_for_late = False

                #policy for half-days
                if rec.half_days_this_month>0 and rec.half_days_this_month%2 == 0 and rec.flag_for_half == False:

                    #First deduct from Casual Leaves if avaialble
                    if remaining_casual > 0:
                        new_entry['holiday_status_id'] = casual_leave_id.id
                        new_entry['name']= "2 Half-Days incurred"
                        update_days = self.env['hr.leave'].create([new_entry])

                        _logger.info('half casual')
                        update_days.number_of_days = math.ceil(update_days.number_of_days_display)
                        update_days.is_sys_generated = True
                        rec.flag_for_half = True
                        break

                    #Then deduct from Annual Leave if available
                    elif att_check_in_month in [1,2,3,4,5,6] and remaining_annual_jan_june > 0:

                        new_entry['holiday_status_id'] = annual_leave_jan_june_id.id
                        new_entry['name']= "2 Half-Days incurred"

                        _logger.info('half annual1\n remaining annual Jan-June leaves: %s', remaining_annual_jan_june)
                        update_days = self.env['hr.leave'].create([new_entry])
                        update_days.number_of_days = math.ceil(update_days.number_of_days_display)
                        update_days.is_sys_generated = True
                        rec.flag_for_half = True
                        break

                    elif att_check_in_month in [7,8,9,10,11,12] and remaining_annual_july_dec > 0:

                        # raise UserError(remaining_annual)
                        new_entry['holiday_status_id'] = annual_leave_july_dec_id.id
                        new_entry['name']= "2 Half-Days incurred"

                        _logger.info('half annual2\nremaining annual Jan-June leaves: %s', remaining_annual_july_dec)
                        update_days = self.env['hr.leave'].create([new_entry])
                        update_days.number_of_days = math.ceil(update_days.number_of_days_display)
                        update_days.is_sys_generated = True
                        rec.flag_for_half = True
                        break

                    #Otherwise count it as an Unpaid Leave
                    else:
                        # raise UserError('in unpaid')

                        unpaid_leave = self.env['hr.leave.type'].search([('is_unpaid','=',True)])

                        new_entry['holiday_status_id'] = unpaid_leave.id
                        new_entry['name']= "2 Half-Days incurred"

                        _logger.info('half unpaid')
                        update_days = self.env['hr.leave'].create([new_entry])
                        update_days.number_of_days = math.ceil(update_days.number_of_days_display)
                        update_days.is_sys_generated = True
                        rec.flag_for_half = True
                        break

                elif rec.half_days_this_month %2 != 0:
                    rec.flag_for_half = False
                    # new_record['date_to'] = date_to
            

class LeaveExt(models.Model):
    _inherit = 'hr.leave'

    is_half_day_request = fields.Boolean(string="Is Half-Day", default=False)

    def refuse_unattended_requests(self):
        unattended_leave_requests = self.env['hr.leave'].search([('state','=','confirm')])

        for request in unattended_leave_requests:
            diff = datetime.datetime.today() - request.create_date
            if diff.days >= 5 :
                request['state'] = 'refuse'