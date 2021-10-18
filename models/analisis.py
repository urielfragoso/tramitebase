
from odoo import models,fields, api
from odoo.exceptions import UserError

class analisistramite(models.Model):
    _name='sol.analisis'

    RefidSolicitud = fields.Many2one(comodel_name='sol.tramite', string='Folio de la Solicitud')
    observaciones = fields.Text(string='Observaciones de Requerimiento')




