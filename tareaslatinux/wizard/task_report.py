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
    }

    def create_task_report(self, cr, uid, ids, task_id, context={}):
        logger = logging.getLogger(__name__)
        fec_reporte = time.strftime("%d de %B de %Y")
        header = 'Reporte Tareas'+';'+ fec_reporte +'\n'*2
        this = self.browse(cr, uid, ids)[0]
        output = header.encode('latin1')
#        targs = self.pool.get('lt.target')
        task = self.pool.get('lt.tarea').browse(cr, uid, [task_id])
#        if not this.target_ids:
#            tids = targs.search(cr, uid, [])
#            targets = targs.browse(cr, uid, tids)
#        else:
#            tarids = [target.id for target in this.target_ids]
#            targids = targs.search(cr, uid, [('id', 'in', tarids)])
#            targets = targs.browse(cr, uid, targids)
#        if not this.date_min:
#            this.date_min = self._get_min_date(cr, uid, ids)
#        if not this.date_max:
#            this.date_min = self._get_max_date(cr, uid, ids)

        ##### HOJA DE REPORTE #####
#        for target in targets:
        #out = ('Nombre objetivo:' + ';' + target.name + '\n'+ ';' + 'Nombre Tarea' + ';'
#            + 'Fecha Tarea' + ';' + 'Pedida por' + ';' + 'Doc. Ref.' + '\n')
#            task_ids = tasks.search(cr, uid, ['&', ('date_create', '>=', this.date_min), '&',
#                                              ('date_create', '<=', this.date_max),
#                                              ('target_id', '=', target.id),
#                                             ]
#                                   )
#            tasks_filter = tasks.browse(cr, uid, task_ids)
#            cont = 0

#        cont += task.tarea_amount_total
        out = (';' + task.name + ';' + task.date_create + ';' + (task.order_by or '')
                + ';' + (task.reference or '') + '\n')
        out += ';'*2 + 'Nombre Recurso' + ';' + 'Cantidad'
        for resource in task.resource_ids:
            out += ';'*2 + resource.name.name_template + ';' + repr(resource.quantity) + '\n'
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
