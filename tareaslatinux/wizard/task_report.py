# -*- coding: latin1 -*-

import base64
from openerp.osv import fields, osv
import time
#import openerp.netsvc as netsvc
import logging

class lt_task_report_wizard(osv.osv_memory):

    _name = "lt.task.report.wizard"
    _description = "Crear Reporte de Tareas"
    _columns = {
            'data': fields.binary('Archivo', readonly=True),
            'name': fields.char('Nombre de Reporte', 64, readonly=False),
            'state': fields.selection([('choose','choose'), ('fin','fin')], string="estado"),
    }

    _defaults = {
            'state': 'choose',
            'name': lambda *a: 'task_report.csv'
    }

    def create_task_report(self, cr, uid, ids, context={}):
        logger = logging.getLogger(__name__)
        fec_reporte = time.strftime("%d de %B de %Y")
        header = 'Reporte Tareas'+';'+ fec_reporte +'\n'*2 + ';'*2 + 'Fecha Tarea' + '\n'
        this = self.browse(cr,uid,ids)[0]
        output = header.encode('latin1')
        targs = self.pool.get('lt.target')
        targids = targs.search(cr,uid,[])
        targets = targs.browse(cr,uid,targids)

        ##### HOJA DE REPORTE #####
        for target in targets:
            out = 'Nombre objetivo:' + ';' + target.name + '\n'
            cont = 0
            for task in target.task_ids:
                cont += task.tarea_amount_total
                out += ';' + 'Tarea:' + ';' + task.name + ';' + task.date_create + '\n'
#                i = 1
                for resource in task.resource_ids:
#                    out += ';'*2 + 'Recurso %i:'%i + ';' + resource.name.name_template + ';' + repr(resource.quantity) + '\n'
                    out += ';'*2 + resource.name.name_template + ';' + repr(resource.quantity) + '\n'
#                    i += 1
            out += ';' + 'Total' + ';'*3 + str(cont) + '\n'*2

            try:
                if isinstance(out, unicode):
                    output += out.encode('latin1')
                else:
                    output += output
            except UnicodeEncodeError:
                logger.warn("""Problemas con caracteres ascii en el objetivo (id: %i),
                               esta linea del reporte se pasa por alto!""" % target.id, exc_info=1)
        try:
            salida = base64.encodestring(output)
        except UnicodeEncodeError:
            logger.warn("Error en el reporte, se deja sin completar!", exc_info=1)
            salida = ''
        print this.name
        dicc = {'state':'fin', 'data': salida, 'name': this.name}
 #       return self.write(cr, uid, ids, {'state':'fin', 'data': salida, 'name': this.name}, context=context )
        return self.write(cr, uid, ids, dicc, context=context)
#        print dicc
        return {'value': dicc}

lt_task_report_wizard()
