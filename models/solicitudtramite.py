
from odoo import models,fields, api
from odoo.exceptions import UserError

class solicitud(models.Model):
    _name='sol.tramite'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # AQUI SE PUEDE HEREDAR MULTIPLES MODELOS Y FUNCIONALIDADES



    telefono = fields.Char(string='Telefono', required=1)
    correo = fields.Char(string='Correo', required=1)
    personavalida = fields.Char(string='Persona Valida', tracking=1, required=1)
    status = fields.Selection([('pendiente', 'Pendiente de enviar'), ('enviado', 'Enviado'), ('notificado', 'Notificado'), ('autorizado', 'Autorizado'),  ('rechazado', 'Rechazado')])
    tipotram = fields.Many2one(comodel_name='cf.tipos.tramites', string='Tipo de Trámite', default=33)
    observaciones = fields.Text(string='Observaciones')

    attachment = fields.Many2many('ir.attachment', 'ir_attach_sol', 'record_relation_sol', 'attachment_id',
                                 string="Documento soporte", tracking=1, required=1)

    estatusjap = fields.Text(compute="_get_estatus")

    correosavisos = fields.Text(compute="_get_correos")

    asesortramite = fields.Text(compute="_get_asesor")

    correosavisosjefes = fields.Text(compute="_get_jefes")

    # FUNCION PARA MOSTRAR LAS ETAPAS EN LA VISTA KANBAN
    def _get_estatus(self):
        usuario = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])

        for company in usuario.company_ids:
            iap = company.partner_id

            for record in self:
                refidsol = record.id

                filtros = [('RefIdIAP', '=', iap.id), ('RefIdTipoTram', '=', 33), ('RefidSolicitud', '=', refidsol)]
                estatusjap_obj = self.env['tramite.gestion.base'].sudo().search(filtros)

                if estatusjap_obj:
                    record.estatusjap = str(estatusjap_obj.EstatusTram)
                else:
                    record.estatusjap = 'Pendiente'

    #CORREOS PARA QUIEN SE MANDA EL OFICIO
    def _get_correos(self):
       for record in self:
        user_id = self.env.uid
        usuario = self.env['res.users'].sudo().search([('id', '=', user_id)])

        for company in usuario.company_ids:
            iap = company.partner_id

            filtros = [('partner_iap_id', '=', iap.id), ('tipotramite_id', '=', 33)]
            user_obj = self.env['usuarios.tramite'].sudo().search(filtros)
            record.correosavisos = user_obj.user_id.login

    #CORREOS JEFES
    def _get_jefes(self):
        for record in self:
            user_id = self.env.uid
            usuario = self.env['res.users'].sudo().search([('id', '=', user_id)])

            for company in usuario.company_ids:
                iap = company.partner_id
                filtros = [('partner_iap_id', '=', iap.id), ('tipotramite_id', '=', 33)]
                jefes_tramite = self.env['jefes.tramite'].sudo().search(filtros)

                records = ''
                for record in jefes_tramite:
                    records+= record.user_id.login+';'

                self.correosavisosjefes = records

    #ASESOR ASIGNADO AL FOLIO
    def _get_asesor(self):
        usuario = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])

        for company in usuario.company_ids:
            iap = company.partner_id
            for record in self:
                refidsol = record.id
                filtros = [('RefIdIAP', '=', iap.id), ('RefIdTipoTram', '=', 33), ('RefidSolicitud', '=', refidsol)]
                asesor_obj = self.env['tramite.gestion.base'].sudo().search(filtros)
                if asesor_obj:
                    record.asesortramite = str(asesor_obj.RefIdUsuario.name)
                else:
                    record.asesortramite = 'Pendiente'


    #FUNCION PARA ENVIAR EL TRAMITE Y REALIZAR EL REGISTRO A GESTION TRAMITES
    def envio_tramite(self):

        for record in self:
            user_id = self.env.uid  # OBTIENE EL ID DE SESION DE LA INSTITUCION QUE ESTA INGRESANDO
            # BUSCA EL USUARIO QUE SE ENCUENTRA EN RES_USERS DE LA IAP
            usuario = self.env['res.users'].sudo().search([('id', '=', user_id)])

            for company in usuario.company_ids:
                iap = company.partner_id

            # HACE UN SELECT A LA TABLA DE USUARIOS TRAMITE, DONDE LA IAP SEA LA QUE ESTA EN SESION Y EL TIPO DE TRAMITE
            # PARA OBTENER EL USUARIO QUE TIENE ASIGNADO PARA ESE TRAMITE
            filtros = [('partner_iap_id', '=', iap.id), ('tipotramite_id', '=', 33)]
            user_obj = self.env['usuarios.tramite'].sudo().search(filtros)

            # SE HACE EL INSERT A LA TABLA DE GESTION DE TRAMITES
            tramite_gestion_obj = self.env['tramite.gestion.base']
            nuevo_registro = {'RefIdIAP': iap.id,
                              'RefIdUsuario': user_obj.user_id.id,
                              'RefIdTipoTram': 33,
                              'EstatusTram': '1',  # 1 : ES LA ETAPA INICIAL DEL TRAMITE
                              'EstatusAsunto': 'activo',
                              'observaciones': '.',
                              'RefidSolicitud': record.id}

            # SE ACTUALIZA EL ESTATUS A ENVIADO EL FOLIO DE LA IAP
            record.write({'status': 'enviado'})
            #SE CREA EL REGISTRO EN TABLA DE GESTION
            id_gestion = tramite_gestion_obj.create(nuevo_registro)

            #SE HACE EL SELECT A LA TABA DE TIEMPOS TRAMITE
            tramite_tiempo_obj = self.env['tiempos.tramite.base']

            nuevo_registro = {'RefIdGestion': id_gestion.id,
                              'Etapa': 1,
                              'Origen': 1
                              }
            tramite_tiempo_obj.create(nuevo_registro)

        # GESTION DE TRAMIGES GENERAL
            tramite_gestion_obj_GRAL = self.env['tramite.gestion']
            nuevo_registro = {'RefIdIAP': iap.id,
                              'RefIdUsuario': user_obj.user_id.id,
                              'RefIdTipoTram': 33,
                             'EstatusAsunto': 'activo',
                              'RefidSolicitud': record.id}

            tramite_gestion_obj_GRAL.create(nuevo_registro)

            # MANDA A LLAMAR TEMPLATE PARA EL ENVIO DE CORREO
            template = self.env.ref('tramitebase.solicitud_correo_base')
            template.send_mail(self.id, force_send=True)

    @api.model
    def create(self,vals):
        vals['status'] = 'pendiente'

        return super(solicitud,self).create(vals)

    #VALIDA PARA QUE NO SE PUEDA MODIFICAR EL REGISTRO CUANDO ESTE YA FUE ENVIADO POR LA INSTITUCION
    def write(self, vals):

        try:
            existe_doc =  vals['attachment']
        except:
            if not self.attachment:
                raise UserError('Es necesario adjuntar la documentación necesaria write')


        # self:  el argumento self trae todos los campos, con los valores nuevos como si fuera la primera vez
        # self._origin: este objeto trae todos los campos con los valores antiguos
        user_id = self.env.uid  # obtiene el id en sesión

        filtro_solicitud_enviada = [('tipotram', '=', self.tipotram.id),
                                    ('create_uid', '=', user_id),
                                    ('id', '=', self.id)
                                    ]
        solicitudenviado_obj = self.env['sol.tramite'].sudo().search(filtro_solicitud_enviada)

        if solicitudenviado_obj.status == 'enviado':
            raise UserError(('No puede modificar un registro enviado'))
        elif solicitudenviado_obj.status == 'autorizado':
            raise UserError(('Su solicitud ya fue autorizada, motivo por el cual no puede ser modificada'))
        elif solicitudenviado_obj.status == 'rechazado':
            raise UserError(('Su solicitud fue rechazada, por favor verifique con su asesor.'))
        return super(solicitud, self).write(vals)


    #FUNCION PARA VER EL REQUERIMIENTO
    def ver_requerimiento(self):
        requerimiento_obj = self.env['sol.requerimiento'].search([('RefidSolicitud', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'oficio de requerimiento base',
            'res_model': 'sol.requerimiento',
            'res_id': requerimiento_obj.id if requerimiento_obj else False,
            'view_mode': 'form',
            'view_id': self.env.ref('tramitebase.requerimiento_IAP_form_view').id,
            'context': {'default_RefidSolicitud': self.id},
            'target': 'current'
        }

    # FUNCION PARA VER EL REQUERIMIENTO
    def ver_resultado(self):
        refidsolicitud = self.id

        for record in self:
            user_id = self.env.uid  # OBTIENE EL ID DE SESION DE LA INSTITUCION QUE ESTA INGRESANDO
            # BUSCA EL USUARIO QUE SE ENCUENTRA EN RES_USERS DE LA IAP
            usuario = self.env['res.users'].sudo().search([('id', '=', user_id)])

            for company in usuario.company_ids:
                refidiap = company.partner_id
                # SI EL FOLIO DE LA IAP ESTA NOTIFICADO,
                filtros = [('RefIdIAP', '=', refidiap.id),
                           ('RefIdTipoTram', '=', self.tipotram.id),
                           ('RefidSolicitud', '=', refidsolicitud),
                           ('create_uid', '=', user_id)]
                solicitudresultado_obj = self.env['tramite.gestion.base'].sudo().search(filtros)
                if solicitudresultado_obj:
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Resultado del tramite',
                        'res_model': 'tramite.gestion.base',
                        'res_id': solicitudresultado_obj.id if solicitudresultado_obj else False,
                        'view_mode': 'form',
                        'view_id': self.env.ref('tramitebase.finaliza_tramite_lectura_form_view').id,
                        'context': {'default_RefidSolicitud': self.id},
                        'target': 'current'
                    }

    #FUNCION PARA RESPONDER EL OFICIO DE REQUERIMIENTO
    def responder_requerimiento(self):
        refidsolicitud = self.id

        for record in self:
            user_id = self.env.uid  # OBTIENE EL ID DE SESION DE LA INSTITUCION QUE ESTA INGRESANDO
            # BUSCA EL USUARIO QUE SE ENCUENTRA EN RES_USERS DE LA IAP
            usuario = self.env['res.users'].sudo().search([('id', '=', user_id)])

            for company in usuario.company_ids:
                refidiap = company.partner_id
                #SI EL FOLIO DE LA IAP ESTA NOTIFICADO,
                filtros = [('RefIdIAP', '=', refidiap.id),
                           ('RefIdTipoTram', '=', self.tipotram.id),
                           ('RefidSolicitud','=',refidsolicitud),
                           ('create_uid','=',user_id)]
                solicitudenviado_obj = self.env['tramite.gestion.base'].sudo().search(filtros)
                if solicitudenviado_obj:
                    solicitudenviado_obj.write({'EstatusTram': '3'})
                    record.write({'status': 'enviado'})
            # MANDA A LLAMAR TEMPLATE PARA EL ENVIO DE CORREO
            template = self.env.ref('tramitebase.requerimiento_respondido')
            template.send_mail(self.id, force_send=True)

    #FUNCION PARA VER LOS TIEMPOS DE REQUERIMIENTO
    def tiempos_tramite(self):
        refidsolicitud = self.id
        #for record in self:
        user_id = self.env.uid  # OBTIENE EL ID DE SESION DE LA INSTITUCION QUE ESTA INGRESANDO
        # BUSCA EL USUARIO QUE SE ENCUENTRA EN RES_USERS DE LA IAP
        usuario = self.env['res.users'].sudo().search([('id', '=', user_id)])

        for company in usuario.company_ids:
            refidiap = company.partner_id
            #SI EL FOLIO DE LA IAP ESTA NOTIFICADO,
            filtros = [('RefIdIAP', '=', refidiap.id),
                       ('RefIdTipoTram', '=', self.tipotram.id),
                       ('RefidSolicitud','=',refidsolicitud),
                       ('create_uid','=',user_id)]
            solicitudenviado_obj = self.env['tramite.gestion.base'].sudo().search(filtros)
            if solicitudenviado_obj:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'tiempos de la solicitud',
                    'res_model': 'tiempos.tramite.base',
                    'res_id': solicitudenviado_obj.id ,
                    'view_mode': 'tree',
                    'view_id': self.env.ref('tramitebase.tiempos_tramite_tree_view').id,
                    'domain': [('RefIdGestion','=', solicitudenviado_obj.id)],
                    'target': 'new'
                }


