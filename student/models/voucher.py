from odoo import models, fields, api, _


class StudentVoucher(models.Model):
    _name = 'student.voucher'
    _description = 'Student Receipt Voucher'

    sequence_number = fields.Char(string='Voucher No.', copy=False, readonly=True)
    today_date = fields.Date(string='Booking Date', default=lambda self: fields.Date.today())
    student_id = fields.Many2one('student.registration', string='Student')
    receipt_type = fields.Selection(
        selection=[('deposit', 'Deposit'), ('bus_fee', 'Bus Fee')],
        string='Receipt Type',
        default='deposit')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, tracking=True, domain="[('type', 'in', ('bank', 'cash'))]")
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.ref('base.INR').id)
    amount = fields.Float(string='Amount', currency_field='currency_id')


    @api.model
    def create(self, vals):
        if vals.get('sequence_number', _('New')) == _('New'):
            vals['sequence_number'] = self.env['ir.sequence'].next_by_code('student.voucher')
        return super(StudentVoucher, self).create(vals)

    def name_get(self):
        res = []
        for record in self:
            name = record.sequence_number
            res.append((record.id, name))
        return res