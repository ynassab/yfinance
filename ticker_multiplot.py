import yfinance as yf
from tkinter import Tk, ttk, Frame, Button, Label
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import date, timedelta
import re

# calendar = ticker.get_calendar()
# calendar = calendar.reset_index() # change index to be actual column
# calendar = calendar.rename(columns={'index':'Key'})
# print(calendar.loc[calendar['Key']=='Earnings Date'])

class Globals():
	pass


def plot_tickers(figsize=(8,6), indicator='Close'):
	
	ticker_names = Globals.category
	
	loading_label['text'] = 'Loading ...'
	root.update()
	
	# destroy the previous plot
	for widget in right_frame.winfo_children():
		widget.destroy()
	
	# make figure
	figure = plt.Figure(figsize=figsize, dpi=100)
	ax = figure.add_subplot(111)
	chart_type = FigureCanvasTkAgg(figure, right_frame)
	chart_type.get_tk_widget().pack()
	
	# load tickers
	for ticker_name in ticker_names:
		
		ticker = yf.Ticker(ticker_name)
		df = ticker.history(start=Globals.start_date_str, end=Globals.end_date_str)
		
		df = df.reset_index()
		for i in ['Open', 'High', 'Close', 'Low']:
			df[i] = df[i].astype('float64')
		
		# convert to percentage change
		df[indicator] = df[indicator].apply(lambda x : 100*(x/df[indicator].iloc[0]-1) )
		
		ax.plot(df['Date'], df[indicator], label=ticker_name)
	
	ax.legend()
	ax.set_xlabel('Date')
	ax.set_ylabel('% Change')
	
	# find category name
	title = [name for name, list in Globals.category_names.items() if list == Globals.category][0]
	ax.set_title(title)

	loading_label['text'] = ''


def change_category(category):
	Globals.category = category
	return plot_tickers()

	
def set_start_date(num_days):
	start_date = Globals.end_date - timedelta(days=num_days)
	Globals.start_date_str = start_date.strftime(Globals.str_format)


def change_period(period):
	pattern = '(\d+)(\w)'
	match = re.match(pattern, period)[0]
	
	if match[1] == 'D':
		multiplier = 1
	elif match[1] == 'M':
		multiplier = 30
	elif match[1] == 'Y':
		multiplier = 365
	
	num_days = int(match[0]) * multiplier
	set_start_date(num_days)
	
	plot_tickers()
	

if __name__ == "__main__":
	
	# set up GUI
	root = Tk()
	root.title('Stock Performance Tracker')
	window_width = 1100
	window_height = 500
	root.geometry("{}x{}".format(window_width, window_height))
	
	left_frame = Frame()
	left_frame.pack(side='left', fill='both')
	right_frame = Frame()
	right_frame.pack(side='right', fill='both')
	
	# set dates
	Globals.str_format = '20%y-%m-%d'
	Globals.end_date = date.today()
	Globals.end_date_str = Globals.end_date.strftime(Globals.str_format)
	set_start_date(365)
	
	# set categories
	canadian_renewables = ['BEP-UN.TO','NPI.TO','INE.TO','BLX.TO','AQN.TO','RNW.TO','HCLN.TO']
	canadian_tech = ['SHOP.TO','CSU.TO','GIB-A.TO','OTEX.TO','LSPD.TO','DSG.TO','BB.TO','KXS.TO','ENGH.TO','DND.TO',
					'CLS.TO','ABST.TO','SW.TO','TCS.TO','ET.TO','PHO.TO','HUT.TO','QTRH.TO','ALYA.TO']
	canadian_tech_1_to_10 = canadian_tech[:10]
	canadian_tech_11_to_19 = canadian_tech[10:]
	canadian_commercial_air_travel = ['AC.TO','CHR.TO','ONEX.TO']
	american_commercial_air_travel = ['AAL','UAL','LUV','DAL','JBLU','ALK']
	vaccine_manufacturers = ['MRNA','PFE','BNTX','JNJ','AZN.L']
	electric_vehicles_1 = ['TSLA','NIO','WKHS','FSR','NKLA','XPEV','LI','BLNK','RIDE','SOLO']
	electric_vehicles_2 = ['QS','GM','GPV.V','GOEV','HYLN','FUV','CHPT','PLUG','KNDI']
	ridesharing = ['UBER','LYFT']
	
	categories = [canadian_renewables, canadian_tech_1_to_10, canadian_tech_11_to_19,
				  canadian_commercial_air_travel, american_commercial_air_travel,
				  vaccine_manufacturers, electric_vehicles_1, electric_vehicles_2, ridesharing]
	
	Globals.category_names = {}
	
	# make category buttons
	for category in categories:
		# get category name
		var_name = [key for key,val in locals().items() if val == category][0]
		# replace underscores with spaces
		text_list = var_name.split('_')
		text_list = [word.capitalize() if word != 'to' else word for word in text_list] # capitalize each word
		text = ' '.join(text_list)	
		
		Globals.category_names[text] = category # the category cannot be the key because it's a list
		
		button = ttk.Button(left_frame, text=text,
							command = lambda category=category : change_category(category))
		button.pack(side='top', anchor='w')
	
	# make loading label
	loading_label = Label(left_frame, text='', font=('Times',12))
	loading_label.pack(side='top', anchor='w')
	
	# make time period buttons
	periods = ['1Y','2Y','3Y','4Y','5Y']
	for period in periods:
		button = Button(left_frame, text=period, command = lambda period=period : change_period(period))
		button.pack(side='left', anchor='s')
	
	
	root.mainloop()
