from flask import Flask, render_template, request
import requests
import psycopg2
from haversine import haversine
from datetime import datetime
import re

app = Flask(__name__) # 初始化 Flask 類別成為 instance

@app.route("/") # 路由和處理函式配對
def index():
    return render_template("index.html")

@app.route("/get-result", methods=["GET"])
def get_result():
	url = "https://maps.googleapis.com/maps/api/staticmap?center="
	center = request.args.get("center")
	zoom = request.args.get("zoom")
	size = request.args.get("size")
	key = request.args.get("key")
	distance = request.args.get("distance")
	url += center + "&zoom=" + zoom + "&size=" + size + "&key=" + key
	img = requests.get(url)
	with open("static/" + center + ".png", "wb") as f:
		f.write(img.content)
	point = (float(request.args.get("lat")), float(request.args.get("lon")))
	conn = psycopg2.connect(database="", user="", password="", host="", port="") # the private information of your database
	cur = conn.cursor()
	result = "<table><tr><th>球賽種類</th><th>日期</th><th>時間</th><th>舉辦地點</th><th>參賽隊伍</th></tr>"
	cur.execute("select * from gamelist;")
	list_all = cur.fetchall()
	current_date = datetime.now()
	for i in list_all:
		p = (float(i[6]), float(i[7]))
		if haversine(point, p) <= float(distance): # km
			reg = re.match(r"\d{4}/\d{1,2}/\d{1,2}", i[1])
			if reg:
				date = datetime.strptime(i[1], "%Y/%m/%d")
				if date.date() >= current_date.date():
					result += "<tr><td>" + i[0] + "</td><td>" + i[1] + "</td><td>" + i[2] + "</td><td>" + i[3] + "</td><td>" + i[4] + " vs. " + i[5] + "</td></tr>"
			else:
				result += "<tr><td>" + i[0] + "</td><td>" + i[1] + "</td><td>" + i[2] + "</td><td>" + i[3] + "</td><td>" + i[4] + " vs. " + i[5] + "</td></tr>"
	result += "</table>"
	conn.commit()
	conn.close()
	return result

if __name__ == "__main__": # 判斷自己執行非被當做引入的模組，因為 __name__ 這變數若被當做模組引入使用就不會是 __main__
	app.debug = True
	app.run()