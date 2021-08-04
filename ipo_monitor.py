# Monitor IPOs on Yahoo Finance
# Yahia Nassab
# May 2021

from urllib.request import urlopen
import re
from tkinter import Tk, ttk, Label, Button, Frame, Entry, END
from pandas import DataFrame, Series
from datetime import date, timedelta
from warnings import warn


class Globals(): # neater than using global keyword
	pass


## fetch data


def find_sunday(given_day):
	for days_back in range(7):
		day = given_day - timedelta(days=days_back)
		# if Sunday
		if day.weekday() == 6:
			Globals.sunday = day
			return


def change_week(how):
	
	if how == "next":
		operator = lambda a,b : a + b
	elif how == "previous":
		operator = lambda a,b : a - b
	
	Globals.sunday = operator(Globals.sunday, timedelta(days=7))
	
	return fetch_week()


def fetch_week():
	
	if Globals.sunday in Globals.cache.keys():
		return update_gui(Globals.cache[Globals.sunday])
	
	all_CAD_matches_df = DataFrame()
	
	for num_days in range(5):
		# fetch monday to friday only
		desired_day = Globals.sunday + timedelta(days=num_days+1)
		desired_day_str = desired_day.strftime(Globals.str_format)
		Globals.loadingLabel["text"] = "Loading data for %s" % desired_day_str
		Globals.root.update()
		CAD_matches_df = fetch_day(desired_day)
		all_CAD_matches_df = all_CAD_matches_df.append(CAD_matches_df)
	
	monday = Globals.sunday + timedelta(days=1)
	friday = Globals.sunday + timedelta(days=5)
	Globals.loadingLabel["text"] = "Presenting data for %s to %s" % (monday, friday)
	
	Globals.cache[Globals.sunday] = all_CAD_matches_df
	
	return update_gui(all_CAD_matches_df)

	
def fetch_day(desired_day):
	
	saturday = Globals.sunday + timedelta(days=6)

	desired_day_str = desired_day.strftime(Globals.str_format)
	sunday_str		= Globals.sunday.strftime(Globals.str_format)
	saturday_str	= saturday.strftime(Globals.str_format)

	url = 'https://ca.finance.yahoo.com/calendar/ipo?from=%s&to=%s&day=%s' % (sunday_str, saturday_str, desired_day_str)
	
	page = urlopen(url)
	html_bytes = page.read()
	html = html_bytes.decode('utf-8')
	
	attribute_pattern = 'aria-label="Symbol".+?>(\w+?\.*\w+?)<\/a>.+?aria-label="Company".+?-->(.+?)<!--.+?aria-label="Exchange".+?-->(.+?)<!--.+?aria-label="Date".+?<span.*?>(.+?)<\/span.+?aria-label="Price Range".+?-->(.+?)<!--.+?aria-label="Price".+?-->(.+?)<!--.+?aria-label="Actions".+?-->(.+?)<!--'
	
	matches = re.findall(attribute_pattern, html)
	
	CAD_matches = []

	for match in matches:
		if match[2] in ["Toronto","TSXV"]:
			CAD_matches.append(match)

	CAD_matches_df = DataFrame(CAD_matches)
	
	return CAD_matches_df


## build GUI


def pack_headers(parent, matches_df, headers):
		if len(matches_df.columns) == len(headers):
			widths = []
			for j,col in enumerate(matches_df.columns):
				full_column = matches_df.iloc[:,j].append(Series(headers[j]))
				widths.append(get_column_width(full_column, Globals.fontsize))
				header_entry = Entry(parent, width=widths[j], font=('Times',Globals.fontsize,'bold'))
				header_entry.grid(row=0, column=j)
				header_entry.insert(END, headers[j])
			return widths
			
		else:
			warn("The number of attributes for table entries do not match the number of headers.")
			return [None]


def get_column_width(series, fontsize, adjustment=0.12):
		num_rows = len(series)
		all_widths = series.apply( lambda x : len(x) )
		width = int( max(all_widths)*fontsize*adjustment )
		return width


def make_table(parent, df, widths):
	num_rows = len(df)
	num_cols = len(df.columns)
	for j in range(num_cols):
		width = widths[j]
		for i in range(num_rows):
			entry = Entry(parent, width=width, font=('Times', Globals.fontsize))
			entry.grid(row=i, column=j)
			entry.insert(END, df.iloc[i,j])


def build_gui():

	Globals.root = Tk()
	Globals.root.title("IPO Monitor")
	
	Globals.frames = []
	num_frames = 4
	for i in range(num_frames):
		Globals.frames.append(Frame(Globals.root))
		Globals.frames[i].pack()
	
	button_fontsize = Globals.fontsize+4
	
	back_button = ttk.Button(Globals.frames[1], text="Prev. Week",
						# font=('Times',button_fontsize),
						command = lambda how="previous" : change_week(how))
	back_button.pack(side="left")
	
	front_button = ttk.Button(Globals.frames[1], text="Next Week",
						# font=('Times',button_fontsize),
						command = lambda how="next" : change_week(how))
	front_button.pack(side="right")
	
	Globals.loadingLabel = Label(Globals.frames[0], text="", 
								font=('Times',Globals.fontsize))
	Globals.loadingLabel.pack()
	
	find_sunday(date.today())
	fetch_week()
	
	Globals.root.mainloop()


def update_gui(matches_df):
	
	# destroy table first, if present
	for frame in [Globals.frames[2], Globals.frames[3]]:
		for widget in frame.winfo_children():
			widget.destroy()
	
	# create new table
	headers = ["Symbol", "Company", "Exchange", "Date", "Price Range", "Price", "Actions"]
	widths = pack_headers(Globals.frames[2], matches_df, headers)
	make_table(Globals.frames[3], matches_df, widths)


if __name__ == "__main__":
		
	Globals.fontsize = 12
	Globals.str_format = "20%y-%m-%d"
	Globals.cache = {}
	
	build_gui()

