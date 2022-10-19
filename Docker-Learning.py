### 服务器间Docker容器迁移
'''
Docker容器迁移到另一台服务器的最常用方法是容器镜像迁移，即容器打包成镜像，压缩镜像，然后复制到另一个服务器解压
step1(打包镜像): docker commit container-id image-name 
step2(压缩镜像): docker save -o image_nxs.tar image_nxs:v1.0
step3(恢复镜像): docker load -i image_nxs.tar
'''

### 进程kill
'''
ps aux | grep python  查看python进程（训练后，GPU还在占用，需要kill掉进程）
ps -ef|grep service  查看service进程（第二列是进程号）
kill  -15  <pid号> 正常杀死进程
kill -9 <pid号> 强制杀死进程

批量清理显卡中残留进程：
sudo fuser -v /dev/nvidia* |awk '{for(i=1;i<=NF;i++)print "kill -9 " $i;}' | sudo sh
清理指定GPU显卡中残留进程，如GPU 2：
sudo fuser -v /dev/nvidia2 |awk '{for(i=1;i<=NF;i++)print "kill -9 " $i;}' | sudo sh

'''
### tmux
'''
一个会话可以用多个窗口，
Ctrl+B -> C 创建一个窗口
Ctrl+B -> P 跳转上一个窗口
Ctrl+B -> N 跳转下一个窗口
Ctrl+B -> W 查看窗口列表
Ctrl+B -> , 给窗口命名
Ctrl+B -> Z 给当前窗格最大化（重新按一次可以恢复）
Ctrl+B -> 上下左右 实现同一个窗口内的不同窗格切换

*窗口切分
Ctrl+B -> “ 水平切分
Ctrl+B -> % 垂直切分

tmux new -s <SessionName>  创建会话
ps aux | grep tmux 查看tmux是否开启服务
Ctrl+B -> D 终端和会话分离开，关掉电脑，会话也一直存在
tumx attach -t <SessionName> 登录上次会话
Ctrl+B -> $ 重新命名会话名字（左下角查看）
Ctrl+B -> S 查看所有会话（上下建选择会话）
tmux ls 查看所有会话
tmux kill-session -t <SessionName>

'''

### tensorboard
ssh -L 16006:127.0.0.1:10066 iotcam@10.14.114.74 -p 4000
'''
跳板：容器6006->服务器10066->本地6006
除了创建docker容器时需要将tensorboard默认6006端口映射到服务器主机端口(这里设置的10066),
还需要将本地端口(这里设置的6006)再使用ssh服务映射到服务器主机端口(这里设置的10066)
'''

### 使用容器运行项目的流程
'''
	Tips: <container id>一般只需要取前几位即可,下同
	Step1: sudo docker ps -a    查看所有容器, 找到你自己的container id ,如果知道id就直接第二步
	Step2: sudo docker start <container id>     启动/重启/终止某个docker容器 <9cbdec9dcf64>
	Step3: sudo docker exec -it -u root <container id> /bin/bash    进入docker容器,交互式终端界面(以root权限进入)
	Step4: exit   退出容器

	Tips：
		docker rm -f <container id>    删除容器
		sudo docker commit -a "nxs" -m "images nxs" 9cbdec9dcf64 images_nxs:v1  将容器打包成镜像
		-a :提交的镜像作者；-m :提交时的说明文字；images_nxs:v1
'''

### 外部电脑使用ssh连接服务器docker内的容器
'''
	sudo docker exec -it $CONTAINER-ID /bin/bash   首先进入docker容器（若已在容器中，则跳过本步骤）
	apt-get update      安装ssh服务
	apt-get install openssh-server

	以下操作均在根目录下进行 (cd /)
	mkdir -p /var/run/sshd  创建目录
	/usr/sbin/sshd -D &    启动ssh服务
	apt-get install net-tools
	netstat -tunlp    查看容器的22端口是否处于监听状态
	apt-get install vim
	sed -ri 's/session    required     pam_loginuid.so/#session    required     pam_loginuid.so/g' /etc/pam.d/sshd  修改SSH服务的安全登录配置，取消pam登录限制

	***下面是避坑重点*** 
	vim /etc/ssh/sshd_config   设置ssh为密码登录
	（i：切换至输入模式，进行编辑；Esc：退出输入模式； :wq 保存并退出）
	（退出不保存命令：当你通过vi/vim更改文件之后，按“Esc“键，退出”insert“模式，然后输入冒号（：）,紧接着输入下面的命令：q!）
	找到地第28行
		# Authentication:
		# LoginGraceTime 2m
		# PermitRootLogin prohibit-password
		# StrictModes yes
	改成：
		# Authentication:
		LoginGraceTime 2m
		PermitRootLogin yes
		StrictModes yes

	passwd (输入新的ssh登录密码） 设置新的ssh登录密码
	service ssh restart  重启ssh服务

	出现“ * Restarting OpenBSD Secure Shell server sshd ”表示ssh服务启动成功   

	至此，ssh服务安装完毕,每次重启容器时，需要开启ssh服务
	/usr/sbin/sshd -D &  开启ssh服务
	service ssh status  查看ssh服务是否开启
	netstat -tunlp  (查看容器的22端口是否处于监听状态)


	以上是服务器端的配置,下面是pycharm配置  
	Step1: https://blog.csdn.net/weixin_42331532/article/details/125492953    配置SSH连接到容器内部
	Step2: https://blog.csdn.net/cocos2dGirl/article/details/114284231        设置容器内部的解释器,为我们执行脚本所用;因为一个环境里有很多python解释器,所以要找到镜像环境所配置的解释器(可通过sys.executable获取)
'''

### Docker从镜像创建容器
sudo nvidia-docker run -p 10088:8888 -p 10022:22 -p 10066:6006 -v /home/workspacex/data:/workspace/data -v /home/workspacex/workspace/nxs/projects:/workspace/projects --shm-size='16g' -w /workspace -it --name experiment_nxs xuesongnie/general:v1.0.0 /bin/bash
'''
	知乎docker配置深度学习环境: https://zhuanlan.zhihu.com/p/64493662

	nvidia-docker: 启动时需要加上nvidia,能调用主机的GPU资源
	run: 创建容器
	-p: 端口映射,15000:22表示将主机的15000端口和容器的22端口绑定
	Tips: 22是ssh端口, 8888是jupyter notebook端口
	-v: 挂载目录,主机目录/home/data和容器目录/workspace/data_dir绑定,容器就可以访问主机目录/home/data下的数据
	--shm-size: 设置共享内存,在训练的时候dataloader要将数据从硬盘读取到内存,如果内存太小,读取训练数据太慢会导致GPU训练效率很慢
	-w: 设置容器主工作目录
	-it: 直接进入交互式
	--name: 设置容器名字
	163d05875b77: 安装镜像的全名或者ID,例如ufoym/deepo:latest
	/bin/bash: 进入交互模式

'''

### Jupyter Notebook
'''
	一、安装Markdown插件,可以阅读.md结尾的文件
	pip install notedown

	通过vim进入配置文件
	vim /root/.jupyter/jupyter_notebook_config.py
	
	添加如下属性
	c.NotebookApp.contents_manager_class = 'notedown.NotedownContentsManager'

'''

### chmod设置文件夹权限
'''
	csdn教程: https://blog.csdn.net/coolcoffee168/article/details/89373902

	1.文件的权限包括读、写、执行,读(read,4),写(write,2),执行r(recute,1)简写即为(r,w,x)
		例如 drwxr-x--- 该权限分为4个部分d、rwx、r-x、---
		d:表示文件类型;
		rwx：表示文件"所有者"的对该文件所拥有的权限;
		r-x：表示文件"所属组"对该文件所拥有的权限;
		---：表示"其他用户"对该文件所拥有的权限。
	2.对某个文件夹更改权限
		sudo chmod -Rf 777 nxs
		表示对文件夹nxs和nxs下的所有文件,设置777权限,即所有人都可以read、write、recute

		-c : 若该文件权限确实已经更改,才显示其更改动作
		-f : 若该文件权限无法被更改也不要显示错误讯息
		-v : 显示权限变更的详细资料
		-R : 对目前目录下的所有文件与子目录进行相同的权限变更(即以递回的方式逐个变更)
		--help : 显示辅助说明
		--version : 显示版本
'''

### docker和linux各种指令
'''
	sudo docker ps -a    查看正在运行和没有运行的容器
'''


### 服务器联网（输入学号+密码）
'''
	sudo vpn-connect -c
'''

### 小技巧：检测路径是否正确
'''
	ls <path>
	正确的话会列出具体的数据
'''

### 清理显卡中的进程
sudo fuser -v /dev/nvidia* |awk '{for(i=1;i<=NF;i++)print "kill -9 " $i;}' | sudo sh

### df -h 显示100%的解决办法
https://blog.csdn.net/yzf279533105/article/details/108490476

### 用netstat网络管理工具查看Linux服务器端口占用
netstat -tunlp|grep 22
