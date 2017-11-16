# -*- coding: utf-8 -*-
# Copyright 2015 Antiun Ingeniería S.L. - Sergio Teruel
# Copyright 2015 Antiun Ingeniería S.L. - Carlos Dauden
# Copyright 2016-2017 Tecnativa - Vicent Cubells
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Project Task Invoice",
    "summary": "Create invoice from project task lines",
    "version": "10.0.1.0.0",
    "category": "Project Management",
    "website": "https://www.cysfuturo.com/",
    "author": "cysfuturo",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "hr_timesheet",
    ],
    "data": [
        "views/hr_timesheet_view.xml",
        "views/project_task_view.xml",
        "views/project_timesheet_view.xml",
        "wizard/create_invoice_wizard.xml",
    ],
}
