# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from setup.models.conf import BaseDao
from setup.models.tasifacte.tasifacte_model import TAsiFacte
from setup.utils import fechas, cadenas

log = logging.getLogger(__name__)


class TasiFacteDao(BaseDao):

    def find_by_claveacceso(self, tfe_claveacceso):
        tasifacte = self.dbsession.query(TAsiFacte).filter(TAsiFacte.tfe_claveacceso == tfe_claveacceso).first()
        return tasifacte

    def find_by_trn_codigo(self, trn_codigo):
        tasifacte = self.dbsession.query(TAsiFacte).filter(TAsiFacte.trn_codigo == trn_codigo).first()
        return tasifacte

    def create_or_update(self, trn_codigo, data):
        tfe_claveacceso = None
        if cadenas.es_nonulo_novacio(data['tfe_claveacceso']):
            tfe_claveacceso = data['tfe_claveacceso']

        tasifacte = self.find_by_trn_codigo(trn_codigo)

        tfe_estado = data['tfe_estado']
        tfe_fecautoriza = data['tfe_fecautoriza']
        tfe_mensajes = data['tfe_mensajes']
        tfe_numautoriza = data['tfe_numautoriza']
        tfe_ambiente = data['tfe_ambiente']
        tfe_estadosri = data['tfe_estadosri']

        if tasifacte is not None:
            if int(tasifacte.tfe_estado) != 1:  # Solo si no esta autorizado se procede a actualizar
                tasifacte.tfe_estado = tfe_estado
                tasifacte.tfe_fecautoriza = tfe_fecautoriza
                tasifacte.tfe_mensajes = tfe_mensajes
                tasifacte.tfe_numautoriza = tfe_numautoriza
                tasifacte.tfe_estadosri = tfe_estadosri
                tasifacte.tfe_claveacceso = tfe_claveacceso if tfe_claveacceso is not None else '_'

                self.dbsession.add(tasifacte)
        else:
            tasifacte = TAsiFacte()
            tasifacte.trn_codigo = trn_codigo
            if tfe_claveacceso is not None:
                tasifacte.tfe_claveacceso = tfe_claveacceso
            tasifacte.tfe_numautoriza = tfe_numautoriza
            tasifacte.tfe_estado = tfe_estado
            tasifacte.tfe_fecautoriza = tfe_fecautoriza
            tasifacte.tfe_ambiente = tfe_ambiente
            tasifacte.tfe_mensajes = tfe_mensajes
            tasifacte.tfe_estadosri = tfe_estadosri

            self.dbsession.add(tasifacte)

        self.commit()

    def get_tipos_estados(self):
        sql = """
        select 0 as est_id, 'TODOS' as est_nombre union
        select est_id, est_nombre from public.testadoscompe
        """
        return self.all(sql, ('est_id', 'est_nombre'))

    def get_form_buscar(self):
        form = {"desde": fechas.get_str_fecha_actual(),
                "hasta": fechas.get_str_fecha_actual(),
                "estado": 0}
        return form

    def buscar_comprobantes(self, form):
        estado = form['estado']
        desde = form['desde']
        hasta = form['hasta']

        wheresql = """
                asifacte.tfe_estado = {0}
                """.format(estado)

        if cadenas.es_nonulo_novacio(desde) and cadenas.es_nonulo_novacio(hasta):
            wheresql += " and (asi.trn_fecreg between '{0}' and '{1}' )".format(fechas.format_cadena_db(desde),
                                                                                fechas.format_cadena_db(hasta))

        sql = """
        select asi.trn_compro, asi.tra_codigo, tra.tra_nombre,
        substring(asi.trn_compro,1,3)||'-'||substring(asi.trn_compro,4,3)||'-'||substring(asi.trn_compro,5) numfact,
        asifacte.tfe_estado,
        asifacte.tfe_numautoriza,
        asifacte.tfe_claveacceso,
        asifacte.tfe_fecautoriza,
        case coalesce(asifacte.tfe_ambiente,0)
           when 1 THEN 'PRUEBAS'
           when 2 THEN 'PRODUCCION'
        ELSE
            'DESCONOCIDO'
        END as ambiente,
        coalesce(est.est_nombre,'NODISPONIBLE') as estado
        from tasiento asi
        join tasifacte asifacte on asi.trn_codigo=asifacte.trn_codigo
        join ttransacc tra  on asi.tra_codigo = tra.tra_codigo
        left join public.testadoscompe est  on est.est_id = asifacte.tfe_estado where {0}
        """.format(wheresql)

        tupla_desc = ('trn_compro',
                      'tra_codigo',
                      'tra_nombre',
                      'numfact',
                      'tfe_estado',
                      'tfe_numautoriza',
                      'tfe_claveacceso',
                      'tfe_fecautoriza',
                      'ambiente',
                      'estado'
                      )

        return self.all(sql, tupla_desc)

    def get_clave_acceso(self, trn_codigo):
        sql = """
        select tfe_claveacceso from tasifacte where trn_codigo = {0}
        """.format(trn_codigo)

        return self.first_col(sql, 'tfe_claveacceso')

    def get_clave_acceso_ambiente(self, trn_codigo):
        sql = """
        select tfe_claveacceso, tfe_ambiente from tasifacte
                           where trn_codigo = {0} 
        """.format(trn_codigo)

        tupla_desc = ('tfe_claveacceso', 'tfe_ambiente')
        return self.first(sql, tupla_desc)
