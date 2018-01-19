import requests,os,json
try:
	import tkinter as tk
except:
	import Tkinter as tk

url = "https://www.instagram.com/"
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0"}

def creating_folder(profile):
	if not os.path.exists(profile):
		print("Creating "+profile+" folder...")
		os.makedirs(profile)
	else:
		for i in range(1,10):			
			profile1 = profile+"("+str(i+1)+")"
			if not os.path.exists(profile1):
				creating_folder(profile1)
				break
		return profile1+"/"
	return profile+"/"
	

def checkusername(username):
	'''Checks requested user exists or not, if yes did he posted anything
	on their wall, if yes then folder created and catch the created path
	from creating_folder and calls the download() with path as parameter'''
	re = requests.get(url+username)
	if(re.status_code==200):
		requestingJSON = requests.get(url+username+"/?__a=1",headers=headers)
		data = requestingJSON.json()
		if not data["user"]["is_private"]:
			if data['user']['media']['count']==0 :
				print("No posts")
			else:
				path = creating_folder(username)
				download(path,data,username)
				print('\n\n************Download Compeleted************')
		else:
			print("Sorry, you are trying to access profile is PRIVATE")


	else:
		print("Invalid profile")

def download(path,jsondata,username):
	'''Filters the media type and calls the appropriate function'''
	collectingNodes = jsondata['user']['media']['nodes']
	try:
		for i in range(12):
			if collectingNodes[i]["__typename"] == "GraphImage" :
				imageurl = collectingNodes[i]['display_src']
				filename = collectingNodes[i]['id']
				download_file(imageurl,filename,path,"image")
			elif collectingNodes[i]["__typename"] == "GraphSidecar" :
				download_array(collectingNodes[i]['code'],path)
			elif collectingNodes[i]['__typename'] == "GraphVideo" :
				download_video(collectingNodes[i]['code'],path)
	except IndexError:
		pass

	has_next = jsondata['user']['media']['page_info']
	has_next_page = has_next['has_next_page']
	if has_next_page :
		restart_cursor = has_next['end_cursor']
		url_rewriting = str(url)+str(username)+'/?__a=1&max_id='+str(restart_cursor)
		fresh_urljson = requests.get(url_rewriting,headers=headers)
		parsed_json = fresh_urljson.json()
		download(path,parsed_json,username)


def download_video(code,path):
	url2=""
	url2 = str(url) + "p/" + str(code) + "/?__a=1"
	requestingJSON2 = requests.get(str(url2),headers=headers)
	data2 = requestingJSON2.json()
	videourl = data2['graphql']['shortcode_media']
	download_file(videourl['video_url'],videourl['id'],path,"video")

def download_file(file_url,filename,path,file_type):
	r = requests.get(file_url,stream=True)
	if file_type == "video" :
		print("Downloading "+filename+".mp4")
		with open(path+filename+".mp4","wb") as f:
			for chunk in r.iter_content(chunk_size=1024):
				f.write(chunk)
	elif file_type == "image" :
		print("Downloading "+filename+".jpg")
		with open(path+filename+".jpg","wb") as f:
			for chunk in r.iter_content():
				f.write(chunk)

def download_array(code,path):
	url1=""
	url1 = str(url) + "p/" + str(code) + "/?__a=1"
	requestingJSON1 = requests.get(str(url1),headers=headers)
	data1 = requestingJSON1.json()
	# print(requestingJSON1)

	fileurl = data1['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']
	try:
		i = 0
		while not fileurl[i]['node']['display_url'] == "":
			download_file(fileurl[i]['node']['display_url'],fileurl[i]['node']['id'],path,"image")
			i+=1
	except IndexError:
		pass




def main():
	app = tk.Tk()

	#Defining the UI
	app.configure(background="#E9BC80")
	app.title("Instagram Media Downloader")
	app.geometry("330x100") #widhtxheight
	app.resizable(False,False) #width, height

	#Creating Widgets
	label = tk.Label(app,text="Enter username in input field")
	label.place(x=80,y=15)

	url = tk.Label(app,text="https://www.instagram.com/")
	url.place(x=10,y=40)

	username = tk.Entry(app)
	username.place(x=170,y=41)

	download = tk.Button(app,text="Download")
	download.place(x=125,y=70)
	download.configure(command=lambda:checkusername(username.get()))

	app.mainloop()

if __name__ == '__main__':
	main()