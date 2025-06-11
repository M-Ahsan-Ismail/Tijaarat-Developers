from odoo import api, fields, models, _, exceptions

from datetime import datetime, date, time, timezone,timedelta
import pytz
from odoo.tools import format_datetime
from odoo.exceptions import UserError, ValidationError


class resourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    in_policy_ids = fields.One2many('working.schedule.in', 'resource_calendar_id')
    out_policy_ids = fields.One2many('working.schedule.out', 'resource_calendar_out_id')

    
class workingScheduleIn(models.Model):
    _name = 'working.schedule.in'
    _description = 'working schedule in'

    sequence = fields.Integer(string='Sequence', default=1)
    resource_calendar_id = fields.Many2one('resource.calendar', ondelete="cascade")
    time_from = fields.Char('From (Duration)')
    time_to = fields.Char('To (Duration)')

    #added the 'Early' status for the time interval of 0800 - 0859 hours
    #has the same effect as the 'Ok' status
    status = fields.Selection([('0', 'OK'),
                               ('1', 'Late'),
                               ('2', 'Half-Day'),
                               ('3', 'Absent'),
                               ('4', 'Early')
                               ])
    


class WorkingScheduleOut(models.Model):
    _name = 'working.schedule.out'
    _description = 'working schedule out'

    sequence = fields.Integer(string='Sequence', default=1)
    resource_calendar_out_id = fields.Many2one('resource.calendar', ondelete="cascade")
    time_from = fields.Char('From (Duration)')
    time_to = fields.Char('To (Duration)')
    status = fields.Selection([('2', 'Half-Day'),
                               ('4', 'Early'),
                               ])
    

class Time_Off_Inherit(models.Model):
    _inherit='hr.leave'

    is_auto=fields.Boolean(string="Is_Auto",readonly=True)
    is_sys_generated = fields.Boolean(string="Is System Generated", default=False)
    
    #inherit the function in order to tackle the issue of 0.5day 
    @api.depends('number_of_days')
    def _compute_number_of_days_display(self):
        for holiday in self:
            if holiday.is_auto:
                holiday.number_of_days = 1.00
                holiday.number_of_days_display = 1.00
            else:
                holiday.number_of_days_display = holiday.number_of_days


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    ### Huzaifa
    description = fields.Char('Description')
    
    is_wfh = fields.Boolean(string="Is WFH", default=False)
    day = fields.Char('Day', compute='compute_day_name')
    status = fields.Selection([('present', 'Present'),
                               ('ok', 'Ok'),
                               ('late', 'Late'),
                               ('half_day', 'Half-Day'),
                               ('absent', 'Absent'),
                               ('early', 'Early'),
                               ('leave', 'Leave'),
                               ('weekend', 'Weekend'),
                               ('holiday', 'Public Holiday'),
                               ], string='Status',compute='_get_status',
                               default='present', store=True)

    DAY_MAPPING = {
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday',
        7: 'Sunday',
    }

    # STATUS_MAPPING = {
    #     '0': 'ok',
    #     '1': 'late',
    #     '2': 'half_day',
    #     '3': 'absent',
    #     '4': 'early',
    # }


    @api.depends('check_in')
    def compute_day_name(self):
        for rec in self:
            rec.day = None
            if rec.check_in:
                day_number = rec.check_in.isoweekday()
                rec.day = self.DAY_MAPPING.get(day_number, 'Unknown')

    def get_weekday(self, day_name):
        return list(self.DAY_MAPPING.values()).index(day_name)



    @api.depends('check_in', 'check_out', 'employee_id')
    def _get_status(self):
        for rec in self:
            status=None

            if rec.check_in:
                user_tz = pytz.timezone( rec.employee_id.tz or 'Asia/Karachi')
                check_in_datetime = pytz.utc.localize(rec.check_in).astimezone(user_tz)
                check_in_hours_t = check_in_datetime.time()

                if rec.employee_id.resource_calendar_id.in_policy_ids:

                    for policy in rec.employee_id.resource_calendar_id.in_policy_ids:
                        
                        if not policy.time_from or not policy.time_to:
                            raise UserError('Time_from or Time_to is missing in any of the policy lines of current employee.')

                        check_in_policy = datetime.strptime(policy.time_from, '%H : %M : %S').time()
                        # check_in_policy_localized = pytz.utc.localize(policy.time_from).astimezone(user_tz)
                        
                        # raise UserError(str([check_in_policy, check_in_hours_t]))

                        check_out_policy = datetime.strptime(policy.time_to, '%H : %M : %S').time()

                        if check_in_policy <= check_in_hours_t <= check_out_policy:
                            
                            status=policy.status
                            # raise UserError(str([check_in_policy, check_in_hours_t, check_out_policy, status]))
                            break
                        else:
                            status = ''
            if rec.check_out:
                user_tz = pytz.timezone(rec.employee_id.tz or 'Asia/Karachi')
                
                check_out_datetime = pytz.utc.localize(rec.check_out).astimezone(user_tz)
                check_out_hours_t=check_out_datetime.time()


                if rec.employee_id.resource_calendar_id.out_policy_ids:
                    for policy in rec.employee_id.resource_calendar_id.out_policy_ids:
                        check_out_policy = datetime.strptime(policy.time_to, '%H : %M : %S').time()
                        if check_out_hours_t <= check_out_policy:
                            status=policy.status
                            break
                

            if status == "0":
                rec['status']= "ok"
            elif status == "1":
                rec['status']= "late"
            elif status == "2":
                rec['status']= "half_day"
            elif status == "3":
                rec['status']= "absent"
            elif status == "4":
                rec['status']= "early"
            else:
                rec['status']= "present"

    def get_status_previous(self):
        for rec in self:
            status = None

            if rec.check_in:
                user_tz = pytz.timezone(rec.employee_id.tz or 'Asia/Karachi')
                check_in_datetime = pytz.utc.localize(rec.check_in).astimezone(user_tz)
                check_in_hours_t = check_in_datetime.time()

                if rec.employee_id.resource_calendar_id.in_policy_ids:

                    for policy in rec.employee_id.resource_calendar_id.in_policy_ids:

                        if not policy.time_from or not policy.time_to:
                            raise UserError(
                                'Time_from or Time_to is missing in any of the policy lines of current employee.')

                        check_in_policy = datetime.strptime(policy.time_from, '%H : %M : %S').time()
                        # check_in_policy_localized = pytz.utc.localize(policy.time_from).astimezone(user_tz)

                        # raise UserError(str([check_in_policy, check_in_hours_t]))

                        check_out_policy = datetime.strptime(policy.time_to, '%H : %M : %S').time()

                        if check_in_policy <= check_in_hours_t <= check_out_policy:

                            status = policy.status
                            # raise UserError(str([check_in_policy, check_in_hours_t, check_out_policy, status]))
                            break
                        else:
                            status = ''
            if rec.check_out:
                user_tz = pytz.timezone(rec.employee_id.tz or 'Asia/Karachi')

                check_out_datetime = pytz.utc.localize(rec.check_out).astimezone(user_tz)
                check_out_hours_t = check_out_datetime.time()

                if rec.employee_id.resource_calendar_id.out_policy_ids:
                    for policy in rec.employee_id.resource_calendar_id.out_policy_ids:
                        check_out_policy = datetime.strptime(policy.time_to, '%H : %M : %S').time()
                        if check_out_hours_t <= check_out_policy:
                            status = policy.status
                            break

            if status == "0":
                rec['status'] = "ok"
            elif status == "1":
                rec['status'] = "late"
            elif status == "2":
                rec['status'] = "half_day"
            elif status == "3":
                rec['status'] = "absent"
            elif status == "4":
                rec['status'] = "early"
            else:
                rec['status'] = "present"
            

    # @api.constrains('check_in', 'check_out', 'employee_id')
    # def _check_validity(self):
    #     """ Verifies the validity of the attendance record compared to the others from the same employee.
    #         For the same employee we must have :
    #             * maximum 1 "open" attendance record (without check_out)
    #             * no overlapping time slices with previous employee records
    #     """
    #     for attendance in self:
    #         # we take the latest attendance before our check_in time and check it doesn't overlap with ours
    #         last_attendance_before_check_in = self.env['hr.attendance'].search([
    #             ('employee_id', '=', attendance.employee_id.id),
    #             ('check_in', '<=', attendance.check_in),
    #             ('id', '!=', attendance.id),
    #         ], order='check_in desc', limit=1)
    #         if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
    #             raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
    #                 'empl_name': attendance.employee_id.name,
    #                 'datetime': format_datetime(self.env, attendance.check_in, dt_format=False),
    #             })
    #
    #         # if not attendance.check_out:
    #         #     # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
    #         #     no_check_out_attendances = self.env['hr.attendance'].search([
    #         #         ('employee_id', '=', attendance.employee_id.id),
    #         #         ('check_out', '=', False),
    #         #         ('id', '!=', attendance.id),
    #         #     ], order='check_in desc', limit=1)
    #         #     if no_check_out_attendances:
    #         #         raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
    #         #             'empl_name': attendance.employee_id.name,
    #         #             'datetime': format_datetime(self.env, no_check_out_attendances.check_in, dt_format=False),
    #         #         })
    #
    #         if not attendance.check_out:
    #                 # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
    #                 no_check_out_attendances = self.env['hr.attendance'].search([
    #                     ('employee_id', '=', attendance.employee_id.id),
    #                     ('check_out', '=', False),
    #                     ('id', '!=', attendance.id),
    #                 ], order='check_in desc', limit=1)
    #
    #                 halfday_time_to =  None
    #                 #We need to get the ha;f-day time policy for the current employee
    #                 for id in self.employee_id.resource_calendar_id.out_policy_ids:
    #                     if id.status == '2': #Accessing the time policy for the Half-Day status
    #                         # halfday_time_to = id.time_to
    #                         halfday_time_to = datetime.strptime(id.time_to, '%H : %M : %S').time()
    #
    #                 if no_check_out_attendances:
    #                     attendance_date = no_check_out_attendances.check_in.date()
    #                     new_check_out = datetime.combine(attendance_date, halfday_time_to)
    #                     no_check_out_attendances.write({
    #                         'check_out': new_check_out - timedelta(hours=5)
    #                     })
    #                     self.env.cr.commit()
    #         else:
    #             # we verify that the latest attendance with check_in time before our check_out time
    #             # is the same as the one before our check_in time computed before, otherwise it overlaps
    #             last_attendance_before_check_out = self.env['hr.attendance'].search([
    #                 ('employee_id', '=', attendance.employee_id.id),
    #                 ('check_in', '<', attendance.check_out),
    #                 ('id', '!=', attendance.id),
    #             ], order='check_in desc', limit=1)
    #             if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
    #                 raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
    #                     'empl_name': attendance.employee_id.name,
    #                     'datetime': format_datetime(self.env, last_attendance_before_check_out.check_in, dt_format=False),
    #                 })

    wfh_reason = fields.Char(string="WFH Reason", compute="_compute_wfh_reason")
    
    @api.depends('employee_id')
    def _compute_wfh_reason(self):
        for rec in self:
            rec.wfh_reason = ''
            if rec.is_wfh:
                wfh_attendances = self.env['wfh_request'].search([('to_date','=',rec.check_out.date()),('from_date','=',rec.check_in.date()),('state','=','approved'),('employee_name', '=', rec.employee_id.id)], limit=1)
                if wfh_attendances:
                    rec.wfh_reason = wfh_attendances.reason