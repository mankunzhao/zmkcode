#coding=UTF-8
import re,urllib,urllib2,socket,os,datetime,sys,time
socket.setdefaulttimeout(20)#sock链接时间限制，超过20即错误
default_start_time = '2013-12-02'
default_end_time = '2013-12-03'

#配置文件中所涉及到的参数
global fileRequire
global IncreLoad
global logFile
global rootDir

#默认配置
fileRequire = ['SESprice.zip','SESprice.dat','SESprifd.dat']
IncreLoad = True
logFile = os.getcwd()+"/logs.txt"
rootDir = os.getcwd()

#配置文件示例,none表示使用默认配置
"""
fileRequire=SESprice.zip,SESprice.dat
IncreLoad=True
logFile=none
rootDir=none
"""

#从配置文件读取配置项
with open(os.getcwd() + '/download.config','r') as rconf:
	for each_line in rconf:
		confTerm = each_line.strip().split('=')
		if confTerm[0] == "IncreLoad":
			if confTerm[1] == "False":
				IncreLoad = False
		elif confTerm[0] == "logFile":
			if confTerm[1] != "none":
				logFile = confTerm[1]
		elif confTerm[0] == "rootDir":
			if confTerm[1] != "none":
				rootDir = confTerm[1]
		elif confTerm[0] == "fileRequire":
			fileRequire = confTerm[1].split(',')
		else:
			continue

try:
	log = open(logFile,'w+')
except:
	print "Open log file error!"
	sys.exit(0)

class DownLoad():
	def __init__(self,start_time=default_start_time,end_time=default_end_time,sfileRequire=fileRequire):
		self.date_range = self.dateRange(start_time,end_time)#日期范围
		self.fileRequire = sfileRequire#文件需求列表
		self.failFileList = []#下载失败的文件列表
		self.dataRootDir = rootDir
	#set the date range that get news
	def dateRange(self,str_start_time,str_end_time):
		"""
		set the date range
		"""
		tmp = str_start_time.split('-')
		tmp1 = str_end_time.split('-')
		start_time = datetime.datetime(int(tmp[0]),int(tmp[1]),int(tmp[2]))
		end_time = datetime.datetime(int(tmp1[0]),int(tmp1[1]),int(tmp1[2]))
		for n in range(int((end_time-start_time).days)):
			yield start_time + datetime.timedelta(n)
	def downloadFile(self,file):
		#尝试下载文件 file是一个三元组(name,url,date)
		try:
			res = urllib2.Request(file[1])
			sock = urllib2.urlopen(res)
			rs = sock.read()
			sock.close()
		except KeyboardInterrupt:#下载文件过程中按Ctr-C退出程序
			print "Stopped By User."
			sys.exit(0)
		except:
		#处理链接打不开的情况（很可能是网络问题）
			self.failFileList.append(file)
			print "Maybe Internet Error.",
			print "-------" + file[0] + "(" + file[2] + ")" + "is added into failFile List for you to choose try again or not."
			return
		if re.match(r"[\d\D]*html",rs):
		#如果返回的是错误页面
			print "This file is not exist(this day is not a weekday or the file is not fabu): " + file[0] + "(" + file[2] + ")"
			return
		else:
			#如果文件存在，开始将文件流写入文件
			#创建文件夹
			if not os.path.exists(self.dataRootDir+os.path.sep+file[2]+os.path.sep):
				os.mkdir(self.dataRootDir+os.path.sep+file[2]+os.path.sep)
			try:
				fileIn = open(self.dataRootDir+ os.path.sep + file[2] + os.path.sep + file[0], 'wb')
				fileIn.write(rs)
			except:
				#写入的过程中出错处理（一般不会发生，所以此时就算文件没写入成功，文件夹还在）
				self.failFileList.append(file)
				print "Something wrong when writting the data to file.",
				print "-------" + file[0] + "(" + file[2] + ")" + "is added into failFile List for you to choose try again or not."
				return
			finally:
				if 'fileIn' in locals(): #如果当前文件正确打开，关闭文件
					fileIn.close()
		#到这下载完成提示
		print file[0] + "(" + file[2] + ")" + " downloaded successfully."
	def work(self):
		print "working..."
		self.dataRootDir = rootDir + os.path.sep + "sgxData"
		#创建文件夹
		if not os.path.exists(self.dataRootDir+os.path.sep):
			os.mkdir(self.dataRootDir+os.path.sep)
		
		fileUrl = 'http://infopub.sgx.com/Apps?A=COW_Prices_Content&B=SecuritiesHistoricalPrice&F=1000&G='
		for tt in self.date_range:
			strDate = str(tt).split(' ')[0]
			print "Get Files From Date:"+strDate
			for filename in self.fileRequire:
				file = (filename,fileUrl + filename + "&H=" + strDate,strDate)
				filePath = self.dataRootDir+os.path.sep+file[2]+os.path.sep+file[0]
				if IncreLoad and os.path.exists(filePath):#文件如果已经存在，不再尝试下载
					print file[0] + " is already exist."
					continue
				self.downloadFile(file)
		#处理下载失败的文件
		while len(self.failFileList) > 0:
			tmpList = self.failFileList[:]
			self.failFileList = []
			print "There are still "+str(len(tmpList))+ " files requires that fail downloaded,try agagin? (y/N)"
			tag = sys.stdin.readline()
			if tag == 'N\n':
				break
			#input 'Y'
			for f in tmpList:
				self.downloadFile(f)

args = sys.argv
argST = default_start_time
argED = default_end_time
if len(args) == 1:
	#download:下今天的
	argST = time.strftime('%Y-%m-%d')
	argED = time.strftime('%Y-%m-%d',time.localtime(time.time()+86400))
else:
	if len(args) == 2:
		if args[1] != "-a" and args[1] != "-help":
			print "commond error,please see -help"
			sys.exit(0)
		if args[1] == "-a":	
			#download -a:下全部的
			argED = time.strftime('%Y-%m-%d',time.localtime(time.time()+86400))
			datetmp = argED.split('-')
			timetmp = time.mktime(datetime.datetime(int(datetmp[0]),int(datetmp[1]),int(datetmp[2])).timetuple())
			argST = time.strftime('%Y-%m-%d',time.localtime(timetmp-86400*29))#往前走29天
		else:
			#download -help:显示帮助
			print "help info of this commond"#命令帮助信息显示
	elif len(args) == 3:
		if args[1] != "-d":
			print "commond error,please see -help"
			sys.exit(0)
		else:
			if not re.match(r"[\d]{4}-[\d]{2}-[\d]{2}$",args[2]):
				print args[2] + " is not a right date format."
				sys.exit(0)
			#download -d 2013-11-01:下指定日期的
			argST = args[2]
			datetmp = args[2].split('-')
			timetmp = time.mktime(datetime.datetime(int(datetmp[0]),int(datetmp[1]),int(datetmp[2])).timetuple())
			argED = time.strftime('%Y-%m-%d',time.localtime(timetmp+86400))
	elif len(args) == 4:
		if args[1] != "-d" and args[1] != "-dx":
			print "commond error,please see -help"
			sys.exit(0)
		else:
			if not re.match(r"[\d]{4}-[\d]{2}-[\d]{2}$",args[2]):
				print args[2] + " is not a right date format."
				sys.exit(0)
			if args[1] == "-d":
				if not re.match(r"[\d]{4}-[\d]{2}-[\d]{2}$",args[3]):
					print args[3] + " is not a right date format."
					sys.exit(0)
				#download -d 2013-11-01 2013-11-02：下区间内的
				argST = args[2]
				datetmp = args[3].split('-')
				timetmp = time.mktime(datetime.datetime(int(datetmp[0]),int(datetmp[1]),int(datetmp[2])).timetuple())
				argED = time.strftime('%Y-%m-%d',time.localtime(timetmp+86400))
			else:
				if not re.match(r"[\d]*$",args[3]):
					print args[3] + " is not a right number format."
					sys.exit(0)
				#download  -dx 2013-11-01 t：下指定日期以后t天的
				argST = args[2]
				datetmp = args[2].split('-')
				timetmp = time.mktime(datetime.datetime(int(datetmp[0]),int(datetmp[1]),int(datetmp[2])).timetuple())
				argED = time.strftime('%Y-%m-%d',time.localtime(timetmp+86400*int(args[3])))
				
	
log.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+": Begin to download files")
D = DownLoad(start_time=argST,end_time=argED)
D.work()
log.close()
