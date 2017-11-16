# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Mentis d.o.o. (<http://www.mentis.si>)
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

{
    "name": "Adds 3 extra sale prices to use as lists A B C",
    "version": "1.0",
    "author": "CYSFuturo S.A.",
    "category": "Sales Management",
    "depends": ['product'],
    "description": """Adds 3 extra sale prices to use as lists A B C, to configure and manage price lists.""",
    "data": [
	    'multiprice_view.xml'
    ],
    "demo_xml": [],
    "active": False,
    "installable": True,
    "website": "http://cysfuturo.com",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
