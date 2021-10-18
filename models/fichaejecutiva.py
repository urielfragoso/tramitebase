
from odoo import models,fields, api
from odoo.exceptions import UserError

class fichaejecutiva(models.Model):
    _name='sol.fichaejecutiva'

    RefidSolicitud = fields.Many2one(comodel_name='sol.tramite', string='Folio de la Solicitud')
    observaciones = fields.Text(string='Observaciones de la Ficha')
    objetoasistencial = fields.Text(compute="_get_objetoiap")



    def _get_objetoiap(self):
        usuario_iap = self.RefidSolicitud.create_uid.company_id
        partner = self.env['res.company'].sudo().search([('id','=',usuario_iap.id)])
        partner_id = partner.partner_id.id

        for objeto in self:
            objetoasistencial_obj = self.env['objetoasistencial'].sudo().search([('partner_id', '=', partner_id)])
            if objetoasistencial_obj:
                objeto.objetoasistencial = str(objetoasistencial_obj.objetoiap)
            else:
                objeto.objetoasistencial = 'Sin Registro'