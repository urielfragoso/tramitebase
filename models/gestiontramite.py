from odoo import models,fields, api,_
from odoo.exceptions import UserError
from odoo.tools.safe_eval import  safe_eval




class tramitesgestion(models.Model):
    _name= 'tramite.gestion.base'
    _rec_name = 'RefIdTipoTram'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    RefIdIAP = fields.Many2one(string='Nombre de la Institucion', comodel_name='res.partner')
    RefIdUsuario = fields.Many2one(comodel_name='res.users', string='Asesor Asignado', domain=[("id",'=','env.uid')])
    RefIdTipoTram =  fields.Many2one(comodel_name='cf.tipos.tramites', string='Tramite realizado')
    EstatusTram = fields.Selection([('1', 'Pendiente'),
                                    ('2', 'Requerimiento'),
                                    ('3', 'Análisis'),
                                    ('4', 'Resultado')],
                                   default="1",
                                   string='Estatus de la Solicitud' ,group_expand='_expand_states')
    EstatusAsunto = fields.Selection([('autorizado','Autorizado'),
                                      ('rechazado', 'Rechazado'),
                                      ('activo', 'Activo')])
    RefidSolicitud = fields.Integer(string='Folio Solicitud')

    fechadocumento = fields.Date(string='Fecha del Oficio')

    observaciones = fields.Text(string="Observaciones del trámite", required=1)

    documentofinal = fields.Many2many('ir.attachment', 'ir_attach_base', 'record_relation_base', 'attachment_id',
                                  string="Oficio de resultado", tracking=1, required=1)

    # ABRE SOLICITUD
    def abrir_folio(self):
        tipotram = self.RefIdTipoTram.id

        return {
                'type': 'ir.actions.act_window',
                'name': 'TRAMITE BASE',
                'res_model': 'sol.tramite',
                'res_id': self.RefidSolicitud,
                'view_mode': 'form',
                'view_id': self.env.ref('tramitebase.solicitud_form_view').id,
                'context': {'default_create_uid': self.RefIdIAP},
                'target': 'current'
            }

    #ABRE OFICIO DE REQUERIMIENTO
    def requerimientoventana(self):
        idtram = self.RefIdTipoTram.id
        print(idtram)

        requerimiento_obj = self.env['sol.requerimiento'].search([('RefidSolicitud', '=', self.RefidSolicitud)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'TRAMITE - REQUERIMIENTO',
            'res_model': 'sol.requerimiento',
            'res_id': requerimiento_obj.id if requerimiento_obj else False,
            'view_mode': 'form',
            'view_id': self.env.ref('tramitebase.requerimiento_form_view').id,
            'context': {'default_RefidSolicitud': self.RefidSolicitud},
            'target': 'current'
        }


    def analisis(self):
        idtram = self.RefIdTipoTram.id
        print(idtram)

        # SE CREA REQUERIMIENTO_OBJ CON EL ID DEL FOLIO SELECCIONADO EN KANBAN
        analisis_obj = self.env['sol.analisis'].search([('RefidSolicitud', '=', self.RefidSolicitud)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Analisis del tramite',
            'res_model': 'sol.analisis',
            'res_id': analisis_obj.id if analisis_obj else False,
            'view_mode': 'form',
            'view_id': self.env.ref('tramitebase.analisistramite_form_view').id,
            'context': {'default_RefidSolicitud': self.RefidSolicitud},
            'target': 'current'
        }


    #ABRE RESULTADO
    def resultado(self):
        idtram = self.RefIdTipoTram
        return {
            'type': 'ir.actions.act_window',
            'name': 'FINALIZA TRAMITE BASE',
            'res_model': 'tramite.gestion.base',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('tramitebase.finaliza_tramite_form_view').id,
            'target': 'current'
        }



    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).EstatusTram.selection]

    def write(self,vals):
        if 'EstatusTram' in vals:
            origen = (self.EstatusTram)
            nueva_etapa = vals['EstatusTram']
            if nueva_etapa < origen:
                raise UserError(('No puede regresar a una etapa anterior'))
            else:
                tramite_tiempo_obj = self.env['tiempos.tramite.base']
                nuevo_registro = {'RefIdGestion': self.id,
                                  'Etapa': nueva_etapa,
                                  'Origen': origen
                                  }
                tramite_tiempo_obj.create(nuevo_registro)
                return super(tramitesgestion, self).write(vals)
        else:
            return super(tramitesgestion, self).write(vals)




    def autorizado(self):
        idtram = self.RefIdTipoTram.id
        #se autoriza en automatico el campo de la tabla tramite.gestion.base
        self.EstatusAsunto = 'autorizado'

        #se autoriza el campo de la tabla de gestion general
        filtros_gral = [('RefidSolicitud', '=', self.RefidSolicitud), ('RefIdTipoTram','=',33)]
        tramite_gestion_obj_GRAL = self.env['tramite.gestion'].sudo().search(filtros_gral)

        if tramite_gestion_obj_GRAL:
            actualiza_estatus = {'EstatusAsunto': 'autorizado'}
            tramite_gestion_obj_GRAL.write(actualiza_estatus)

        #se autoriza el folio de la solicitud
        filtros = [('id', '=', self.RefidSolicitud), ('status', '=', 'enviado')]
        folio_obj = self.env['sol.tramite'].sudo().search(filtros)
            #SE ACTUALIZA EL ESTATUS A ENVIADO EL FOLIO DE LA IAP ESTADOSFIN
        folio_obj.status = 'autorizado'

        return {"view_mode": "kanban",
                    "res_model": "tramite.gestion.base",
                    "type": "ir.actions.act_window",
                    "target": "main",
                    "name":_('Tramite Base'),
                    "view_id":self.env.ref('tramitebase.solicitudes_tramite_kanban_view').id,
                    "context":{'search_default_activo':1}}




    def cancelado(self):
        idtram = self.RefIdTipoTram.id
        #se autoriza en automatico el campo de la tabla de tramite.gestion.base
        self.EstatusAsunto = 'rechazado'

        #se autoriza el campo de la tabla de gestion general
        filtros_gral = [('RefidSolicitud', '=', self.RefidSolicitud), ('RefIdTipoTram', '=', 33)]
        tramite_gestion_obj_GRAL = self.env['tramite.gestion'].sudo().search(filtros_gral)

        if tramite_gestion_obj_GRAL:
            actualiza_estatus = {'EstatusAsunto': 'rechazado'}
            tramite_gestion_obj_GRAL.write(actualiza_estatus)

        #se autoriza el folio de la solicitud
        filtros = [('id', '=', self.RefidSolicitud), ('status', '=', 'enviado')]
        folio_obj = self.env['sol.tramite'].sudo().search(filtros)
        # SE ACTUALIZA EL ESTATUS A ENVIADO EL FOLIO DE LA IAP
        folio_obj.status = 'rechazado'
        return {"view_mode": "kanban",
                "res_model": "tramite.gestion.base",
                "type": "ir.actions.act_window",
                "target": "main",
                "name": _('Tramite Base'),
                "view_id": self.env.ref('tramitebase.solicitudes_tramite_kanban_view').id,
                "context": {'search_default_activo': 1}}






