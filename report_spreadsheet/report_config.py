# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Made.com.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import datetime
from datetime import date
import csv
from tempfile import TemporaryFile
import logging
_logger = logging.getLogger(__name__)
import time
import base64
from tools.safe_eval import safe_eval as eval
from osv import osv, fields
from tools.translate import _
from report_spreadsheet.spreadsheetcreator import SpreadsheetCreator


def enc(s):
    if isinstance(s, unicode):
        return s.encode('utf8')
    return s


def get_csv_format(columns_header, lines_to_export):
    outfile = TemporaryFile('w+')
    writer = csv.writer(outfile, quotechar='"', delimiter=',')
    writer.writerow([enc(x[0]) for x in columns_header])
    for line in lines_to_export:
        writer.writerow([enc(x) for x in line])
    outfile.seek(0)
    file_to_export = base64.encodestring(outfile.read())
    outfile.close()
    return file_to_export


class report_config(osv.osv):
    _name = 'report.config'
    _description = 'Report Export'

    def _get_users(self, cr, uid, ids, field_name, arg, context=None):
        return {}

    def _search_users(self, cr, uid, obj, name, arg, context=None):
        args = []
        if not uid == 1:
            sql = """
            SELECT rcul.report_config_id as id
            FROM report_config_user_rel rcul WHERE rcul.user_id = %s
            """ % uid
            cr.execute(sql)
            ids = cr.fetchall()
            args = [('id', 'in', ids)]
        return args

    _columns = {
        'compute_domain': fields.function(_get_users, type="boolean",
                                          fnct_search=_search_users,
                                          string="Domain for the tree view",
                                          method=True),
        'name': fields.char('Name', size=256, required=True),
        'code': fields.text('Code', required=True),
        'columns_header': fields.text('Columns Header', required=True),
        'user_ids': fields.many2many('res.users', 'report_config_user_rel',
                                     'report_config_id', 'user_id', 'Users'),
        'active': fields.boolean('Active',
                  help="Hide the report if it has not been approved."),
        'param_ids': fields.one2many('report.param', 'report_config_id',
                                     'Parameters'),
        'parameters_enabled': fields.boolean('Parameters enabled?'),
        'report_version_ids': fields.one2many('ir.attachment',
                                              'report_config_id',
                                              'Report Versions'),
        'type_of_format': fields.selection([('.xls', '.xls'),
                                            ('.csv', '.csv')],
                                           string="Format", required=True),
        'message': fields.text(string='Message', readonly=True),
    }

    _defaults = {
        'type_of_format': lambda *a: '.xls',
        'active': False,
        'columns_header': lambda *a: """# Example: columns_header = [ (_('Name'), 'string'), (_('Quantity'), 'number'), (_('Date'), 'string')]
""",
        'code': lambda *a: """# You can use the following variables:
#  - self: ORM model of the record on which the action is triggered
#  - cr: database cursor
#  - uid: current user id
#  - ids: ids of the report wizard
#  - context: current context
#  - date (coming from datetime import date)
# You have to give to "result" something like: [[value_of_the_name1, quantity1, date1], [value_of_the_name2, quantity2, date2], ...]
list_of_lines = []
# your code
result = list_of_lines
""",
    }

    def get_space_header(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return {
                '_': _,
        }

    def get_header(self, cr, uid, ids, message, context=None):
        """
        Return one list of list representing the header of the report.
        """
        if context is None:
            context = {}
        config_values = self.read(cr, uid, ids[0], ['columns_header'], context)
        space_header = self.get_space_header(cr, uid, ids, context)
        try:
            expr_header = config_values['columns_header']
            eval(expr_header, space_header,
                 mode='exec', nocopy=True)  # nocopy allows to return 'result'
        except Exception, e:
            del(space_header['__builtins__'])
            message += """
            Something went wrong when generating the report: %s
            """ % (e,)
        columns_header = space_header.get('columns_header', [])
        return columns_header, message

    def get_space_code(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return {
                'self': self,
                'cr': cr,
                'uid': uid,
                'ids': ids,
                'context': dict(context),
                'date': date,
        }

    def get_list_of_lines(self, cr, uid, ids, message, context=None):
        """
        Return list of lists representing the values of each line of the report.
        """
        if context is None:
            context = {}
        config_values = self.read(cr, uid, ids[0], ['code'], context)
        space_code = self.get_space_code(cr, uid, ids, context)
        try:
            expr_code = config_values['code']
            eval(expr_code, space_code,
                 mode='exec', nocopy=True)  # nocopy allows to return 'result'
        except Exception, e:
            del(space_code['__builtins__'])
            message += """
            Something went wrong when generating the report: %s.
            """ % (e,)
        list_of_lines = space_code.get('result', False)
        return list_of_lines, message

    def generate_report(self, cr, uid, ids, context=None):
        """
        Write the results in a csv or xls file.
        """
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        message = ''
        start_time = time.time()
        config_values = self.read(cr, uid, ids[0], ['code', 'columns_header', 'name', 'type_of_format'], context)
        columns_header, message = self.get_header(cr, uid, ids, message, context)
        list_of_lines, message = self.get_list_of_lines(cr, uid, ids, message, context)
        type_of_format = config_values['type_of_format']
        if not list_of_lines:
            return self.write(cr, uid, ids,
                              {'message': message or 'The report did not return anything'},
                              context)
        lines_to_export = []
        for line in list_of_lines:
            if len(line) < len(columns_header):
                lines_to_export.append(line + ['' for x in range(len(columns_header)-len(line))])
            else:
                lines_to_export.append(line)
        filename_config = config_values['name']
        if type_of_format == '.xls':
            file_to_export = SpreadsheetCreator('Returns_report', columns_header, lines_to_export)
            file_exported = base64.encodestring(file_to_export.get_xml(default_filters=['decode.utf8']))
            filename = '%s_%s.xls' % ('_'.join(filename_config.split()).replace('-', '_'), datetime.datetime.utcnow().strftime('%Y_%m_%d'))
        elif type_of_format == '.csv':
            file_exported = get_csv_format(columns_header, lines_to_export)
            filename = '%s_%s.csv' % ('_'.join(filename_config.split()).replace('-', '_'), datetime.datetime.utcnow().strftime('%Y_%m_%d'))
        end_time = time.time()
        message += '\n Report created in %s seconds. Check the last attachment.' % (round(end_time - start_time))
        self.write(cr, uid, ids, {'message': message}, context)
        if file_exported:
            self.save_report_in_attachment(cr, uid, ids, file_exported, filename, context)
        return True

    def save_report_in_attachment(self, cr, uid, ids, file_exported, filename, context):
        """
        Version the reports
        """
        vals = {'report_config_id': ids[0],
                'name': filename,
                'datas': file_exported,
                'datas_fname': filename,
                'res_id': False}
        return self.pool.get('ir.attachment').create(cr, uid, vals, context)

    def copy_data(self, cr, uid, single_id, default=None, context=None):
        if not default:
            default = {}
        if not context:
            context = {}
        vals_to_read = ['name']
        read_vals = self.read(cr, uid, single_id, vals_to_read, context)
        default['report_version_ids'] = []
        default['name'] = "%s (copy)" % read_vals['name']
        default['message'] = ""
        return super(report_config, self).copy_data(cr, uid, single_id,
                                                    default=default,
                                                    context=context)

report_config()
