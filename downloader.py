import os,json
try:
	import requests
except ImportError:
	os.system('pip install requests')
	# import requests
try:
	import tkinter as tk
except:
	import Tkinter as tk


class Instagram(object):
	def __init__(self,profile,login_user,login_password):
		self.url = "https://www.instagram.com/"
		self.profile = profile
		self.user_id = login_user
		self.password = login_password
		self.header = {
			"User-Agent":"Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0"
		}

	def checkusername(self):
		'''Checks requested user exists or not, if yes did he posted anything
		on their wall, if yes then folder created and catch the created path
		from creating_folder and calls the download() with path as parameter'''
		re = requests.get(self.url+self.profile)
		if(re.status_code==200):
			requestingJSON = requests.get(self.url+self.profile+"/?__a=1",headers=self.header)
			data = requestingJSON.json()
			if not data["user"]["is_private"]:
				if data['user']['media']['count']==0 :
					print("No posts")
				else:
					path = self.creating_folder(self.profile)
					self.download(path,data,'public')
					print('\n\n************Download Compeleted************')
			else:
				if self.user_id=='user name' or self.user_id=='' and self.password=='password' or self.password=='':
					print("Sorry, you are trying to access profile is PRIVATE...")
					print('Login required')
				else:
					global private
					private = PRIVATE_PROFILE(self.user_id,self.password)
					global privatelogin
					privatelogin = private.login()
					if privatelogin == False:
						print("Invalid username or password")
					else:
						privatejson = private.return_json(privatelogin,self.profile,'','')
						if privatejson['user']['followed_by_viewer'] == False:
							print("You don't have previliges to access "+self.profile+" profile")
						else:
							path = self.creating_folder(self.profile)
							self.download(path,privatejson,'private')
							print('\n\n************Download Compeleted************')
		else:
			print("Invalid profile")

	def creating_folder(self,folder):
		if not os.path.exists(folder):
			print("Creating "+folder+" folder...")
			os.makedirs(folder)
		else:
			for i in range(1,10):			
				newfolder = folder+"("+str(i+1)+")"
				if not os.path.exists(newfolder):
					self.creating_folder(newfolder)
					break
			return newfolder+"/"
		return folder+"/"
		


	def download(self,path,jsondata,status):
		'''Filters the media type and calls the self.appropriate function'''
		collectingNodes = jsondata['user']['media']['nodes']
		try:
			for i in range(12):
				if collectingNodes[i]["__typename"] == "GraphImage" :
					imageurl = collectingNodes[i]['display_src']
					filename = collectingNodes[i]['id']
					self.download_file(imageurl,filename,path,"image")
				elif collectingNodes[i]["__typename"] == "GraphSidecar" :
					self.download_array(collectingNodes[i]['code'],path,status)
				elif collectingNodes[i]['__typename'] == "GraphVideo" :
					self.download_video(collectingNodes[i]['code'],path,status)
		except IndexError:
			pass

		has_next = jsondata['user']['media']['page_info']
		has_next_page = has_next['has_next_page']
		if has_next_page :
			restart_cursor = has_next['end_cursor']
			if status == 'public':
				url_rewriting = str(self.url)+str(self.profile)+'/?__a=1&max_id='+str(restart_cursor)
				fresh_urljson = requests.get(url_rewriting,headers=self.header)
				parsed_json = fresh_urljson.json()
				self.download(path,parsed_json,'public')
			elif status == 'private':
				fresh_urljson = private.return_json(privatelogin,self.profile,'',str(restart_cursor))
				self.download(path,fresh_urljson,'private')


	def download_video(self,code,path,status):
		url2=""
		url2 = str(self.url) + "p/" + str(code) + "/?__a=1"
		if status == 'public':
			requestingJSON2 = requests.get(str(url2),headers=self.header)
			data2 = requestingJSON2.json()
		elif status == 'private':
		 	data2 = private.return_json(privatelogin,self.profile,url2,'')

		videourl = data2['graphql']['shortcode_media']
		self.download_file(videourl['video_url'],videourl['id'],path,"video")

	def download_file(self,file_url,filename,path,file_type):
		r = requests.get(file_url,stream=True)
		if file_type == "video" :
			print("Downloading "+filename+".mp4")
			with open(path+filename+".mp4","wb") as f:
				for chunk in r.iter_content(chunk_size=2048):
					f.write(chunk)
		elif file_type == "image" :
			print("Downloading "+filename+".jpg")
			with open(path+filename+".jpg","wb") as f:
				for chunk in r.iter_content(chunk_size=2048):
					f.write(chunk)

	def download_array(self,code,path,status):
		url1=""
		url1 = str(self.url) + "p/" + str(code) + "/?__a=1"
		if status == 'public':
			requestingJSON1 = requests.get(str(url1),headers=self.header)
			data1 = requestingJSON1.json()
		elif status == 'private':
			data1 = private.return_json(privatelogin,self.profile,url1,'')

		fileurl = data1['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']
		try:
			i = 0
			while not fileurl[i]['node']['display_url'] == "":
				self.download_file(fileurl[i]['node']['display_url'],fileurl[i]['node']['id'],path,"image")
				i+=1
		except IndexError:
			pass

class PRIVATE_PROFILE(object):
	def __init__(self,user,password):
		self.privateuser_id = user
		self.privatepassword = password

	def login(self):
		sess = requests.Session()
		sess.headers.update({
			'Accept': '*/*',
			'Accept-Encoding' : 'gzip, deflate',
			'Accept-Language' : 'en-US;q=0.6,en;q=0.4',
			'authority': 'www.instagram.com',
			'ContentType' : 'application/x-www-form-urlencoded',
			'Connection': 'keep-alive',
			'Host' : 'www.instagram.com',
			'origin': 'https://www.instagram.com',
			'Referer': 'https://www.instagram.com',
			'UserAgent':'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
			'x-instagram-ajax':'1',
			'X-Requested-With': 'XMLHttpRequest'
		})
		r = sess.get('https://www.instagram.com/') 
		sess.headers.update({'X-CSRFToken' : r.cookies.get_dict()['csrftoken']})
		r = sess.post('https://www.instagram.com/accounts/login/ajax/', data={'username':self.privateuser_id, 'password':self.privatepassword}, allow_redirects=True)
		sess.headers.update({'X-CSRFToken' : r.cookies.get_dict()['csrftoken']})
		loginstatus = json.loads(r.text)
		if loginstatus['authenticated'] == True :
			print('Login Success')
			return sess
		elif loginstatus['authenticated'] == False :
			return False

	def return_json(self,sess,profile,url,max_id):
		if not url=='':
			r = sess.get(url)
		else:
			r = sess.get('https://www.instagram.com/'+profile+'/?__a=1&max_id='+max_id)
		return r.json()


class GUI(object):
	def __init__(self):
		self.app = tk.Tk()
		self.labels()


	def labels(self):
		#Defining the UI
		self.app.configure(background="#E9BC80")
		self.app.title("Instagram Media Downloader")
		self.app.geometry("330x170") #widhtxheight
		self.app.resizable(False,False) #width, height

		#Creating Widgets
		label = tk.Label(self.app,text="Instagram Downloader")
		label.place(x=80,y=15)

		url = tk.Label(self.app,text="https://www.instagram.com/")
		url.place(x=10,y=40)

		profilename = EntryWithPlaceholder(self.app)
		profilename.insert(0,'profile_id')
		profilename.place(x=170,y=41)

		login = tk.Label(self.app,text="Login(optional)")
		login.place(x=120,y=70)

		login_user = EntryWithPlaceholder(self.app)
		login_user.insert(0,'user name')
		login_user.place(x=30,y=100)

		login_password = EntryWithPlaceholder(self.app)
		login_password.insert(0,'password')
		login_password.place(x=170,y=100)

		download = tk.Button(self.app,text="Download")
		download.place(x=120,y=130)
		download.configure(command=lambda:Instagram(profilename.get(),login_user.get(),login_password.get()).checkusername())


	def startTktinter(self):
		self.app.mainloop()


class EntryWithPlaceholder(tk.Entry):
    def __init__(self,master=None, placeholder='', color='grey'):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()
if __name__ == '__main__':
	start = GUI()
	start.startTktinter()