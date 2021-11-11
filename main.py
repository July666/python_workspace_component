#!/usr/bin/python
# coding=utf-8
import paramiko
import xlrd
import time
import os
import handle_file

server_info_list = handle_file.read_excel_xlsx('documents/server_info.xlsx', 'Sheet1')
Host = server_info_list[0][0]
Port = server_info_list[0][1]
Username = server_info_list[0][2]
Password = server_info_list[0][3]

def ssh_exec_cmd():
    '''ssh远程登录：windows客户端连接Linux服务器，并输入指令'''
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #连接Linux服务器
    #ssh.connect('10.20.24.89', 22, 'root', 'Cfcs2@07380')
    ssh.connect(Host, Port, Username, Password)


    #执行Linux相关命令
    #不管环境上是否存在kafka进程，都kill -9 kafka进程
    stdin, stdout, stderr = ssh.exec_command("ps -ef | grep kafka | grep -v grep | awk '{print $2}' | xargs kill -9")
    #不管环境上是否存在zookeeper进程，都kill -9 zookeeper进程
    stdin, stdout, stderr = ssh.exec_command("ps -ef | grep zookeeper | grep -v grep | awk '{print $2}' | xargs kill -9")
    # 不管环境上是否存在redis进程，都kill -9 redis进程
    stdin, stdout, stderr = ssh.exec_command("ps -ef | grep redis | grep -v grep | awk '{print $2}' | xargs kill -9")
    # 不管环境上是否存在nginx进程，都kill -9 nginx进程
    stdin, stdout, stderr = ssh.exec_command("ps -ef | grep nginx | grep -v grep | awk '{print $2}' | xargs kill -9")
    """
    解压zookeeper安装包，并启动zookeeper服务
    """
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local && rm -rf zookeeper " )
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local && unzip -o zookeeper-3.4.12.zip -d /usr/local ")
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local && mv zookeeper-3.4.12 zookeeper && chmod -R 777 zookeeper ")
    stdin, stdout, stderr = ssh.exec_command("source .bash_profile; sh /usr/local/zookeeper/bin/zkServer.sh start ")
    time.sleep(3)
    """
    解压kafka安装包，并修改kafka配置文件，然后启动kafka服务
    """
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local && rm -rf kafka ")
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local && unzip -o kafka_2.11-0.11.0.3.zip -d /usr/local")
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local && mv kafka_2.11-0.11.0.3 kafka && chmod -R 777 kafka")
    #修改kafka配置文件
    # stdin, stdout, stderr = ssh.exec_command("cd /usr/local/kafka/config; sed -i 's#zookeeper.connect=.*#zookeeper.connect=10.20.158.33:2181#g' server.properties")
    # stdin, stdout, stderr = ssh.exec_command("cd /usr/local/kafka/config; sed -i 's#listeners=.*#listeners=PLAINTEXT://10.20.158.33:9092#g' server.properties")
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local/kafka/config; sed -i " + "'" + "s#zookeeper.connect=.*#zookeeper.connect=" + Host + ":2181#g" + "'" + " server.properties")
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local/kafka/config; sed -i " + "'" + "s#listeners=.*#listeners=PLAINTEXT://" + Host + ":9092#g" + "'" + " server.properties")
    #启动kafka服务
    stdin, stdout, stderr = ssh.exec_command("source .bash_profile; sh /usr/local/kafka/bin/kafka-server-start.sh -daemon /usr/local/kafka/config/server.properties")
    time.sleep(3)

    """
    解压redis安装包，并修改redis.conf配置文件，然后启动redis服务
    """
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local && rm -rf redis ")
    print("删除redis文件夹")
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local && tar xzvf redis-4.0.14.tar.gz -C /usr/local" ,get_pty=True)
    time.sleep(3)
    print("成功解压redis包")
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local && mv redis-4.0.14 redis && chmod -R 777 redis")
    print("redis文件夹赋予权限777")
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local/redis && make > log_make.log", get_pty=True)
    time.sleep(100)
    print("make命令执行结束")
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local/redis && make install PREFIX=/usr/local/redis > log_makeinstall.log", get_pty=True)
    time.sleep(100)
    print("make install命令执行结束")
    # 修改redis.conf配置文件
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local/redis && sed -i " + "'" + "s#bind 127.0.0.1#bind " +'"' + Host +'"' + "#g' redis.conf", get_pty=True)
    time.sleep(5)
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local/redis && sed -i 's/# requirepass .*/requirepass taredis/g' redis.conf", get_pty=True)
    time.sleep(5)
    print("修改redis.conf文件成功")
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local/redis/bin ; ./redis-server ../redis.conf >> redis.log 2>&1 &")
    time.sleep(5)
    print("启动redis服务成功")

    """
    解压nginx安装包
    """
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local && rm -rf nginx")
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local && tar xzvf nginx-1.12.2.tar.gz -C /usr/local", get_pty=True)
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local && mv nginx-1.12.2 nginx && chmod -R 777 nginx")
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local/nginx; ./configure --prefix=/usr/local/nginx --conf-path=/usr/local/nginx/nginx.conf > log_configure.log", get_pty=True)
    time.sleep(3)
    err = stderr.readlines()
    #out = stdout.readlines()
    print("./configure命令输出结果打印开始:")
    if (err):
        print('error:')
        print(err)
    # else:
    #     print('out:')
    #     print(out)
    print("./configure命令输出结果打印结束!")
    print("ending")
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local/nginx; make > log_make.log", get_pty=True)
    time.sleep(30)
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local/nginx; make install > log_make_install.log", get_pty=True)
    time.sleep(30)
    #将环境变量/etc/profile中删除包含的NGINX_HOME变量的行
    stdin, stdout, stderr = ssh.exec_command("sed -i '/export NGINX_HOME=/d' /etc/profile")
    #将环境变量/etc/profile中使用到$NGINX_HOME变量的地方删除，主要目的是删除;$NGINX_HOME/sbin字符串
    stdin, stdout, stderr = ssh.exec_command("sed -i 's#;$NGINX_HOME/sbin##g' /etc/profile")
    #在环境变量/etc/profile中添加NGINX_HOME变量
    stdin, stdout, stderr = ssh.exec_command("sed -i '/export PATH=/i\export NGINX_HOME=/usr/local/nginx' /etc/profile")
    #在环境变量PATH路径末尾添加;$NGINX_HOME/sbin内容
    stdin, stdout, stderr = ssh.exec_command("sed -i 's#export PATH=.*#&;$NGINX_HOME/sbin#g' /etc/profile")
    #本地上传一份nginx.conf模板，并修改里面的IP信息
    ###############################
    sftp_upload_file()
    ###############################
    #修改nginx.conf配置文件
    stdin, stdout, stderr = ssh.exec_command("cd /usr/local/nginx/conf; sed -i " + "'" + "s#server   10.20.24.89#server   " + Host + "#g' nginx.conf", get_pty=True)
    time.sleep(5)
    stdin, stdout, stderr = ssh.exec_command("source /etc/profile; /usr/local/nginx/sbin/nginx -c /usr/local/nginx/conf/nginx.conf", get_pty=True)
    time.sleep(5)
    err = stderr.readlines()
    #out = stdout.readlines()
    if (err):
        print('error:')
        print(err)
    # else:
    #     print('out:')
    #     print(out)
    print("ending")
    ssh.close()

def sftp_upload_file():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #ssh.connect(Host, Port, Username, Password)
    #连接Linux服务器
    ssh.connect(Host, Port, Username, Password)
    transport = paramiko.Transport((Host, Port))
    transport.banner_timeout = 10
    transport.connect(username=Username, password=Password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    try:
        sftp.put('./documents/nginx.conf', '/usr/local/nginx/conf/nginx.conf')
        print("上传成功")
    except Exception as e:
        print(e)
    transport.close()
if __name__ == '__main__':
    ssh_exec_cmd()