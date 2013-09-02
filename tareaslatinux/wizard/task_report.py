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
            'report_file': fields.char('Report Name', 64, readonly=False),
            'data': fields.binary('Report', readonly=True),
            'state': fields.selection([('choose','choose'), ('fin','fin')], string="state"),
    }

    def create_task_report(self, cr, uid, ids, context={}):
        logger = logging.getLogger(__name__)
        fec_reporte = time.strftime("%d de %B de %Y")
        header = 'Tasks Report'+';'+ fec_reporte +'\n'*2
        output = header.encode('latin1')
        this = self.browse(cr, uid, ids)[0]
        task = self.pool.get('lt.tarea').browse(cr, uid, context['active_ids'])[0]
        date = time.strftime('%d/%m/%Y', time.strptime(task.date, '%Y-%m-%d %H:%M:%S'))
        if task.date_deadline:
            date_deadline = time.strftime('%d/%m/%Y', time.strptime(task.date_deadline, '%Y-%m-%d %H:%M:%S'))
        else:
            date_deadline = 'not set'
        if task.date_finish or task.date_cancel:
            date_finish = time.strftime('%d/%m/%Y', time.strptime((task.date_finish or task.date_cancel), '%Y-%m-%d %H:%M:%S'))
        else:
            date_finish = 'not set'
        out = (';' + 'Name' + ';' + 'Description' + ';' + 'Created Date' + ';' +
               'Deadline' + ';' + 'Terminated Date' + ';'+ 'Order by' +
               ';' + 'Ref. Doc.' + ';' + 'State' + '\n' + ';' + unicode(task.name) +
               ';' + unicode(task.description or '') + ';' + date + ';' + date_deadline +
               ';' + date_finish + ';' + unicode(task.order_by or '') + ';' +
               unicode(task.reference or '') + ';' + task.state + '\n' + ';' +
               'Resource Name' + ';' + 'Quantity')

        for resource in task.resource_ids:
            out += ('\n'+';' + unicode(resource.name.name_template) + ';' +
                    unicode(str(resource.quantity)))
        out += '\n'+ ';' + 'Total Task ($):' + ';' + str(task.tarea_amount_total).replace('.', ',') + '\n'*2

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
