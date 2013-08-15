# -*- coding: latin1 -*-

import base64
import time

from openerp.osv import fields, osv
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
        date = time.strftime('%d/%m/%Y', time.strptime(task.date, '%Y-%m-%d %H:%M:%S'))
        date_deadline = time.strftime('%d/%m/%Y', time.strptime(task.date_deadline, '%Y-%m-%d %H:%M:%S'))
        date_finish = time.strftime('%d/%m/%Y', time.strptime((task.date_finish or task.date_cancel), '%Y-%m-%d %H:%M:%S'))
        out = (';' + 'Nombre' + ';' + 'Fecha creada' + ';' + 'Fecha planificada' +
               ';' + 'Fecha cumplida' + ';'+ 'Pedida por' + ';' + 'Doc. Ref.' + ';' +
               'Estado' + '\n' + ';' + unicode(task.name) + ';' + date + ';' +
               date_deadline + ';' + date_finish +
               ';' + unicode(task.order_by or '') + ';' + unicode(task.reference or '') +
               ';' + task.state + '\n' + ';'*2 + 'Nombre Recurso' + ';' + 'Cantidad')
        for resource in task.resource_ids:
            out += ('\n'+';'*2 + unicode(resource.name.name_template) + ';' +
                    unicode(str(resource.quantity)))
        out += '\n'+';' + 'Total Tarea:' + ';'*5 + '$' + str(task.tarea_amount_total) + '\n'*2

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
