from odoo import fields, models, api
from datetime import datetime, timedelta
import numpy as np



class tiempostramitegestion(models.Model):
    _name = 'tiempos.tramite.base'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    RefIdGestion = fields.Many2one(comodel_name='tramite.gestion.base', string='Tiempos por etapa')
    Etapa = fields.Integer(string='Etapa')
    Origen = fields.Integer(string='Origen')

    dias_etapa = fields.Integer(compute="_dias_proceso")
    nombre_etapa = fields.Text(compute="_nombre_etapa")
    dias_tramite = fields.Integer(compute="_dias_tramite")

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

                    calculo_dias = ( b - a).days
                    res = np.busday_count(a.strftime('%Y-%m-%d'), b.strftime('%Y-%m-%d'),
                                          weekmask=[1, 1, 1, 1, 1, 0, 0])
            else:
                if etapa_obj.Origen ==1:
                    a = datetime.date(idgestion.create_date)
                    b = datetime.date(etapa_obj.create_date)

                    calculo_dias = (b - a).days
                    res = np.busday_count(a.strftime('%Y-%m-%d'), b.strftime('%Y-%m-%d'),
                                          weekmask=[1, 1, 1, 1, 1, 0, 0])
                else:

                    filtro = [('Etapa', '=',etapa_obj.Origen),('RefIdGestion','=',idgestion.id)]
                    etapa_inicial_calculo = self.env['tiempos.tramite.base'].sudo().search(filtro)
                    a = datetime.date(etapa_inicial_calculo.create_date)
                    b = datetime.date(etapa_obj.create_date)
                    calculo_dias = ( b - a).days

                    res = np.busday_count(a.strftime('%Y-%m-%d'), b.strftime('%Y-%m-%d'),
                                          weekmask=[1, 1, 1, 1, 1, 0, 0])
            record.dias_etapa = res





    def _dias_tramite(self):
        idgestion = self.RefIdGestion.id
        #obtiene la fecha inicial de la primera etapa
        filtro = [('RefIdGestion', '=', idgestion), ('Etapa', '=', 1)]
        etapa_inicial_calculo = self.env['tiempos.tramite.base'].sudo().search(filtro)
        #se crea variable con la fecha inicial
        a = datetime.date(etapa_inicial_calculo.create_date)

        #se obtienen los registros de todas las etapas
        filtro = [('RefIdGestion', '=', idgestion)]
        fecha_etapa = self.env['tiempos.tramite.base'].sudo().search(filtro)

        #se obtiene el ultimo registro de self
        ultimo_reg = (self.ids.pop())


        for record in fecha_etapa:

            if record.id == ultimo_reg:

                b = datetime.now()
                res = np.busday_count(a.strftime('%Y-%m-%d'), b.strftime('%Y-%m-%d'), weekmask=[1, 1, 1, 1, 1, 0, 0])
            else:

                b = datetime.date(record.create_date)


                #se contabilizan los dias sin fines de semana
                res = np.busday_count(a.strftime('%Y-%m-%d'), b.strftime('%Y-%m-%d'),weekmask=[1,1,1,1,1,0,0])

            record.dias_tramite = res

