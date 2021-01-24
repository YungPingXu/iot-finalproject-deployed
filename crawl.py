import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import psycopg2
from datetime import datetime

current_date = datetime.now()

def write_data(name, gamedate, gametime, place, team1, team2):
	conn = psycopg2.connect(database="", user="", password="", host="", port="") # the private information of your database
	cur = conn.cursor()
	cur.execute("SELECT COUNT(*) FROM gamelist WHERE name='" + name + "' and gamedate='" + gamedate + "' and gametime='" + gametime + "' and location='" + place + "' and team1='" + team1 + "' and team2='" + team2 + "';")
	row = cur.fetchall()
	if row[0][0] == 0:
		print("new")
		url = 'https://maps.googleapis.com/maps/api/geocode/json'
		params = {'key': '', 'address': place} # your key
		r = requests.get(url, params=params)
		results = r.json()['results']
		location = results[0]['geometry']['location']
		cur.execute("INSERT INTO gamelist VALUES ('" + name + "','" + gamedate + "','" + gametime + "','" + place + "','" + team1 + "','" + team2 + "'," + str(location['lat']) + "," + str(location['lng']) + ");")
	conn.commit()
	conn.close()

def Pleague():
	print("Crawling the P-league website...")
	url = "https://pleagueofficial.com/schedule-regular-season"
	res = requests.get(url)
	res.encoding = "utf-8"
	soup = BeautifulSoup(res.text, "html.parser")
	for i in soup.find_all("div", {"class": "row mx-0"}):
		text = list(i.stripped_strings)
		if len(text) in (21, 22): # if len(text) == 21 or len(text) == 22
			write_data("P-league", text[0], text[2], text[10], text[4], text[17]) # 日期,時間,舉辦地點,參賽隊伍1,參賽隊伍2

def SBL():
	print("Crawling the SBL website...")
	url = "https://sleague.tw/gameList.html"
	driver = webdriver.Chrome() # 啟動瀏覽器
	driver.get(url) # 取得網頁原始碼
	sleep(1)
	driver.refresh() # 重新刷新網頁
	sleep(1)
	driver.refresh() # 重新刷新網頁
	sleep(2)
	soup = BeautifulSoup(driver.page_source, "html.parser")
	table = soup.find("table", {"class": "table table-hover same-bg"}).find("tbody")
	sleep(1)
	driver.quit() # 關閉瀏覽器
	for i in table.find_all("tr"):
		text = list(i.stripped_strings)
		team = str(text[4]).replace("\t", "").replace("\n", " ").replace(" ", "").split("vs.")
		date = datetime.strptime(text[1], "%Y/%m/%d")
		if date.date() >= current_date.date():
			write_data("SBL", text[1], text[2], text[3], team[0], team[1]) # 日期,時間,舉辦地點,參賽隊伍1,參賽隊伍2

def TVL():
	print("Crawling the TVL website...")
	url = "http://tvl.ctvba.org.tw/fixtures-results/"
	res = requests.get(url)
	res.encoding = "utf-8"
	soup = BeautifulSoup(res.text, "html.parser")
	table = soup.find("div", {"class": "sportspress sp-widget-align-left"}).find("div", {"class": "sp-template sp-template-event-blocks"}).find("div", {"class": "sp-table-wrapper"}).find("table", {"class": "sp-event-blocks sp-data-table sp-paginated-table"}).find("tbody")
	for i in table.find_all("tr"):
		link = i.find("h4", {"class": "sp-event-title"}).a["href"] # 再對爬到的網址連結進行爬蟲 也就是爬兩層
		rsp = requests.get(link)
		rsp.encoding = "utf-8"
		sp = BeautifulSoup(rsp.text, "html.parser")
		tr = sp.find("table", {"class": "sp-event-details sp-data-table sp-scrollable-table"}).find("tbody").find("tr")
		text = list(tr.stripped_strings)
		location = sp.find("table", {"class": "sp-data-table sp-event-venue"}).find("thead").find("tr")
		team = sp.find("header", {"class": "entry-header"}).text.strip().split(" vs ")
		date = datetime.strptime(text[0], "%Y/%m/%d")
		if date.date() >= current_date.date():
			write_data("TVL", text[0], text[1], location.text.strip(), team[0], team[1]) # 日期,時間,舉辦地點,參賽隊伍1,參賽隊伍2

SBL()
TVL()
Pleague()