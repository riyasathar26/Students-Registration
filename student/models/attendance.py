from odoo import models, fields, api, exceptions, _
import datetime

class StudentAttendance(models.Model):
    _name = 'student.attendance'

    student_id = fields.Many2one('student.registration', string='Student')
    current_status = fields.Char(string='Current Status', compute='_compute_current_status', store=True)

    show_check_in_button = fields.Boolean(compute='_compute_show_buttons')
    show_check_out_button = fields.Boolean(compute='_compute_show_buttons')

    attendance_record_ids = fields.One2many('student.attendance.record', 'student_id', string='Attendance Records')


    @api.depends('student_id.attendance_status')
    def _compute_show_buttons(self):
        for record in self:
            record.show_check_in_button = record.student_id.attendance_status == 'checked_out'
            record.show_check_out_button = record.student_id.attendance_status == 'checked_in'


    @api.depends('student_id.attendance_status', 'student_id.attendance_records')
    def _compute_current_status(self):
        for record in self:
            if record.student_id:
                status = record.student_id.attendance_status
                if status == 'checked_in':
                    record.current_status = f'{record.student_id.name}, Click to Check Out'
                elif status == 'checked_out':
                    record.current_status = f'{record.student_id.name}, Click to Check In'
                else:
                    record.current_status = ''
            else:
                record.current_status = ''

    def action_checkin(self):
        if not self.student_id:
            raise exceptions.UserError(_('Please select a student for check-in.'))

        student = self.student_id
        if student.attendance_status == 'checked_out':
            # Perform check-in action
            self.with_context(force_checkin=True).action_student_checkin(student.id)

            self.student_id = False

            # Create attendance record
            self.env['student.attendance.record'].create({
                'student_id': student.id,
                'checkin_time': fields.Datetime.now(),
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    def action_checkout(self):
        if not self.student_id:
            raise exceptions.UserError(_('Please select a student for check-out.'))

        student = self.student_id
        if student.attendance_status == 'checked_in':
            # Perform check-out action
            student.with_context(force_checkout=True).action_student_checkout()

            self.student_id = False

            # Update the corresponding attendance record with checkout time
            attendance_record = self.env['student.attendance.record'].search(
                [('student_id', '=', student.id), ('checkout_time', '=', False)],
                order='checkin_time desc',
                limit=1
            )
            if attendance_record:
                attendance_record.write({'checkout_time': fields.Datetime.now()})
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    @api.model
    def action_student_checkin(self, student_id):
        student = self.env['student.registration'].browse(student_id)
        if student.attendance_status == 'checked_out':
            student.write({
                'checkin_time': fields.Datetime.now(),
                'attendance_status': 'checked_in'
            })

