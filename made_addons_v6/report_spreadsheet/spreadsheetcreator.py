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

from tools.misc import file_open
from mako.template import Template


class SpreadsheetCreator(object):
    def __init__(self, title, headers, datas):
        self.headers = headers
        self.datas = datas
        self.title = title

    def get_xml(self, default_filters=[]):
        f, filename = file_open('addons/report_spreadsheet/report/spreadsheet_writer_xls.mako', pathinfo=True)
        f[0].close()
        tmpl = Template(filename=filename, input_encoding='utf-8', output_encoding='utf-8', default_filters=default_filters)
        return tmpl.render(objects=self.datas, headers=self.headers, title= self.title)
