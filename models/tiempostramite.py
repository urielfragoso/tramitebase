from odoo import fields, models, api
from datetime import  datetime



class tiempostramitegestion(models.Model):
    _name = 'tiempos.tramite.base'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    RefIdGestion = fields.Many2one(comodel_name='tramite.gestion.base', string='Tiempos por etapa')
    Etapa = fields.Integer(string='Etapa')
    Origen = fields.Integer(string='Origen')

    dias_etapa = fields.Integer(compute="_dias_proceso")
    nombre_etapa = fields.Text(compute="_nombre_etapa")

    def _nombre_etapa(self):
        for record in self:
            if record.Etapa ==2:
                record.nombre_etapa = 'Requerimiento'
            elif record.Etapa ==3:
                record.nombre_etapa = 'Analisis'
            elif record.Etapa ==4:
                record.nombre_etapa = 'Etapa Final'
            elif record.Etapa ==1:
                record.nombre_etapa = 'Etapa Inicial'



    def _dias_proceso(self):
        idgestion = self.RefIdGestion

        for record in self:
            idtabla = record.ids
            filtro = [('id', '=', idtabla), ('RefIdGestion','=',idgestion.id)]
            etapa_obj = self.env['tiempos.tramite.base'].search(filtro)


            if etapa_obj.Etapa == 2:
                if etapa_obj.Origen == 1:
                    a = datetime.date(idgestion.create_date)
                    b = datetime.date(etapa_obj.create_date)
                    calculo_dias = ( b - a)
            else:
                if etapa_obj.Origen ==1:
                    a = datetime.date(idgestion.create_date)
                    b = datetime.date(etapa_obj.create_date)
                    calculo_dias = (b - a)
                else:

                    filtro = [('Etapa', '=',etapa_obj.Origen),('RefIdGestion','=',idgestion.id)]
                    etapa_inicial_calculo = self.env['tiempos.tramite.base'].sudo().search(filtro)
                    a = datetime.date(etapa_inicial_calculo.create_date)
                    b = datetime.date(etapa_obj.create_date)
                    calculo_dias = ( b - a)
            record.dias_etapa = calculo_dias.days





































