# -*- coding: latin1 -*-

import base64

from openerp.osv import fields, osv
import time
import logging

class lt_task_report_wizard(osv.osv_memory):
    _name = "lt.task.report.wizard"
    _description = "Crear Reporte de Tareas"

    def default_get(self, cr, uid, ids, fields, context={}):
        file1 = 'task_report.csv'
        res = {'state': 'choose', 'report_file': file1}
        return res

    _columns = {
            'report_file': fields.char('Nombre de Reporte', 64, readonly=False),
            'data': fields.binary('Reporte', readonly=True),
            'state': fields.selection([('choose','choose'), ('fin','fin')], string="estado"),
    }

    def create_task_report(self, cr, uid, ids, context={}):
        logger = logging.getLogger(__name__)
        fec_reporte = time.strftime("%d de %B de %Y")
        header = 'Reporte Tareas'+';'+ fec_reporte +'\n'*2
        output = header.encode('latin1')
        this = self.browse(cr, uid, ids)[0]
        task = self.pool.get('lt.tarea').browse(cr, uid, context['active_ids'])[0]
        out = (';' + task.name + ';' + task.date_create + ';' + (task.order_by or '')
                + ';' + (task.reference or '') + '\n')
        out += ';'*2 + 'Nombre Recurso' + ';' + 'Cantidad'
        for resource in task.resource_ids:
            out += ';'*2 + resource.name.name_template + ';' + str(resource.quantity) + '\n'
        out += ';' + 'Total Tarea:' + ';'*5 + '$' + str(task.tarea_amount_total) + '\n'*2

        try:
            if isinstance(out, unicode):
                output += out.encode('latin1')
            else:
                output += out
        except UnicodeEncodeError:
            logger.warn("""Problemas con caracteres ascii en el objetivo (id: %i),
                           esta linea del reporte se pasa por alto!""" % task.id, exc_info=1)
        salida = base64.encodestring(output)
        return self.write(cr, uid, ids,
                          {'state': 'fin', 'data': salida, 'report_file': this.report_file},
                          context=context)

lt_task_report_wizard()
