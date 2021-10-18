
from odoo import models,fields, api
from odoo.exceptions import UserError

class oficioRequerimiento(models.Model):
    _name='sol.requerimiento'

    RefidSolicitud = fields.Many2one(comodel_name='sol.tramite', string='Folio de la Solicitud')
    observaciones = fields.Text(string='Observaciones de Requerimiento')
    fechadocumento = fields.Date(string='Fecha del Oficio', required=1)
    estatus = fields.Selection([('pendiente', 'Pendiente de Notificar'),
                                    ('notificado', 'Notificado')],
                                   default="pendiente",
                                   string='Oficio de requerimiento' ,group_expand='_expand_states')

    oficiorequerimiento = fields.Many2many('ir.attachment', 'ir_attach_req', 'record_relation_req', 'attachment_id',
                                  string="Oficio de Requerimiento", tracking=1, required=1)

    def notificariap(self):
        refidsolicitud = self.RefidSolicitud.id
        for record in self:
            filtros = [('id', '=', refidsolicitud),('status','=','enviado')]
            folio_obj = self.env['sol.tramite'].sudo().search(filtros)

            #SE ACTUALIZA EL ESTATUS A ENVIADO EL FOLIO DE LA IAP
            folio_obj.write({'status':'notificado'})

        record.write({'estatus': 'notificado'})


        template = self.env.ref('tramitebase.solicitud_requerimiento')
        template.send_mail(self.id, force_send=True)
