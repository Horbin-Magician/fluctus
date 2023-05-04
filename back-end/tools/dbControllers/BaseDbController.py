import sqlite3


class BaseDbController():
  # 初始化
  def __init__(self):
    # 连接数据库，提供两种路径
    try:
      self.conn = sqlite3.connect('datas/base.db')
    except:
      self.conn = sqlite3.connect('back-end/datas/base.db')
    self.c = self.conn.cursor()
  # 关闭数据库
  def __del__(self):
    self.conn.close()
  # 初始化数据库
  def initDb(self):
    self.c.execute('''CREATE TABLE USER
    (USERNAME   TEXT  PRIMARY KEY   NOT NULL,
    PASSWORD   TEXT                 NOT NULL,
    AUTHORITY  TEXT);''')
    self.c.execute('''CREATE TABLE AUTHORITY
    (NAME      TEXT   PRIMARY KEY   NOT NULL,
    MENUS      TEXT);''')
  # 更新用户信息
  def updateUser(self, username, password='', authority=''):
    query,data = '',[]
    datas = self.getUserData(username)
    if(len(datas) == 0):# username不存在时，添加用户
      query = '''INSERT INTO USER (USERNAME,PASSWORD,AUTHORITY) VALUES (?,?,?)'''
      data = [username, password, authority]
      self.c.execute(query, data)
    else:# username存在时，更新密码和权限
      if(password != ''):
        query = '''UPDATE USER SET PASSWORD=(?) WHERE USERNAME=(?)'''
        data = [password, username]
        self.c.execute(query, data)
      if(authority != ''):
        query = '''UPDATE USER SET AUTHORITY=(?) WHERE USERNAME=(?)'''
        data = [authority, username]
        self.c.execute(query, data)
    self.conn.commit()
  # 删除User
  def delUser(self, username):
    query = 'DELETE FROM USER WHERE USERNAME=(?)'
    data = [username]
    self.c.execute(query, data)
    self.conn.commit()
  # 更新权限
  def updateAuthority(self, name, menus=''):
    query,data = '',[]
    datas = self.getAuthorityData(name)
    if(len(datas) == 0):# 权限类不存在时，添加权限类
      query = '''INSERT INTO AUTHORITY (NAME,MENUS) VALUES (?,?)'''
      data = [name, menus]
    else:# 权限类存在时，更新权限
      query = '''UPDATE AUTHORITY SET MENUS=(?) WHERE NAME=(?)'''
      data = [menus, name]
    self.c.execute(query, data)
    self.conn.commit()
  # 删除权限
  def delAuthority(self, name):
    query = 'DELETE FROM AUTHORITY WHERE NAME=(?)'
    data = [name]
    self.c.execute(query, data)
    self.conn.commit()
  # 获取数据
  def getData(self, tableName):
    query = 'SELECT * FROM ' + tableName
    cursor = self.c.execute(query)
    datas = []
    for cow in cursor:
      datas.append(cow)
    return datas
  # 获取用户数据
  def getUserData(self, userName=None):
    if(userName == None):
      return self.getData('USER')
    query = 'SELECT * FROM USER WHERE USERNAME=(?)'
    data = [userName]
    cursor = self.c.execute(query, data)
    datas = []
    for cow in cursor:
      datas.append(cow)
    return datas
  # 获取权限数据
  def getAuthorityData(self, name=None):
    if(name == None):
      return self.getData('AUTHORITY')
    query = 'SELECT * FROM AUTHORITY WHERE NAME=(?)'
    data = [name]
    cursor = self.c.execute(query, data)
    datas = []
    for cow in cursor:
      datas.append(cow)
    return datas


# test code
if __name__ == '__main__':
  bDb = BaseDbController()