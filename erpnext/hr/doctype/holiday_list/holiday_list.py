# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import add_days, add_years, cint, getdate
from frappe.model.naming import make_autoname
from frappe import msgprint, throw, _
import datetime

from frappe.model.document import Document

class HolidayList(Document):
	def autoname(self):
		self.name = make_autoname(self.fiscal_year + "/" + self.holiday_list_name + "/.###")
		
	def validate(self):
		self.update_default_holiday_list()
	
	def get_weekly_off_dates(self):
		self.validate_values()
		yr_start_date, yr_end_date = self.get_fy_start_end_dates()
		date_list = self.get_weekly_off_date_list(yr_start_date, yr_end_date)
		last_idx = max([cint(d.idx) for d in self.doclist.get(
			{"parentfield": "holiday_list_details"})] or [0,])
		for i, d in enumerate(date_list):
			ch = self.append('holiday_list_details', {})
			ch.description = self.weekly_off
			ch.holiday_date = d
			ch.idx = last_idx + i + 1

	def validate_values(self):
		if not self.fiscal_year:
			throw(_("Please select Fiscal Year"))
		if not self.weekly_off:
			throw(_("Please select weekly off day"))

	def get_fy_start_end_dates(self):
		return frappe.db.sql("""select year_start_date, year_end_date
			from `tabFiscal Year` where name=%s""", (self.fiscal_year,))[0]

	def get_weekly_off_date_list(self, year_start_date, year_end_date):
		from frappe.utils import getdate
		year_start_date, year_end_date = getdate(year_start_date), getdate(year_end_date)
		
		from dateutil import relativedelta
		from datetime import timedelta
		import calendar
		
		date_list = []
		weekday = getattr(calendar, (self.weekly_off).upper())
		reference_date = year_start_date + relativedelta.relativedelta(weekday=weekday)
			
		while reference_date <= year_end_date:
			date_list.append(reference_date)
			reference_date += timedelta(days=7)
		
		return date_list
	
	def clear_table(self):
		self.set('holiday_list_details', [])

	def update_default_holiday_list(self):
		frappe.db.sql("""update `tabHoliday List` set is_default = 0 
			where ifnull(is_default, 0) = 1 and fiscal_year = %s""", (self.fiscal_year,))
