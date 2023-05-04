import sqlite3


class FavouritesDbController():
  # 初始化
  def __init__(self):
    try:
      self.conn = sqlite3.connect('datas/favourites.db')
    except:
      self.conn = sqlite3.connect('back-end/datas/favourites.db')
    self.c = self.conn.cursor()
  # 关闭数据库
  def __del__(self):
    self.conn.close()
  # 初始化数据库
  def initDb(self):
    self.c.execute('''CREATE TABLE TYPE
    (TITLE   TEXT  PRIMARY KEY   NOT NULL,
    RANK     INT                 NOT NULL);''')
    self.c.execute('''CREATE TABLE ITEM
    (URL      TEXT   PRIMARY KEY   NOT NULL,
    TYPE     TEXT                NOT NULL,
    TITLE    TEXT                NOT NULL,
    RANK     INT                 NOT NULL,
    ICONURL  TEXT,
    DESCRIPTION TEXT);''')
  # 更新类别
  def updateType(self, title, rank, oldTitle=None):
    query, data = '', []
    if(oldTitle):# 若oldTitle不为空，更新信息
      if(rank):
        query = '''UPDATE TYPE SET RANK=(?) WHERE TITLE=(?)'''
        data = [rank, oldTitle]
        self.c.execute(query, data)
      if(title):
        query = '''UPDATE TYPE SET TITLE=(?) WHERE TITLE=(?)'''
        data = [title, oldTitle]
        self.c.execute(query, data)
    else:# 若oldTitle为空
      datas = self.getTypeData(title)
      if(len(datas) == 0):
        query = '''INSERT INTO TYPE (TITLE,RANK) VALUES (?,?)'''
        data = [title, rank]
        self.c.execute(query, data)
      else:
        query = '''UPDATE TYPE SET RANK=(?) WHERE TITLE=(?)'''
        data = [rank, title]
        self.c.execute(query, data)
    self.conn.commit()
  # 删除类别
  def delType(self, title):
    delData = self.getTypeData(title)
    types = self.getTypeData()
    # 删除type
    query = 'DELETE FROM TYPE WHERE TITLE=(?)'
    data = [title]
    self.c.execute(query, data)
    # 删除所属type的item
    query = 'DELETE FROM ITEM WHERE TYPE=(?)'
    data = [title]
    self.c.execute(query, data)
    self.conn.commit()
    # 更新之后type的排序
    for type in types:
      if(type[1] > delData[0][1]):
        self.updateType(type[0], type[1]-1)
  # 获取type数据，若title为空，返回所有
  def getTypeData(self, title=None):
    cursor = None
    if(title == None):
      query = 'SELECT * FROM TYPE ORDER BY RANK ASC'
      cursor = self.c.execute(query)
    else:
      query = 'SELECT * FROM TYPE WHERE TITLE=(?)'
      data = [title]
      cursor = self.c.execute(query, data)
    datas = []
    for cow in cursor:
      datas.append(cow)
    return datas
  # 移动type
  def moveTypeData(self, mvFrom, mvTo):
    datas = self.getTypeData()
    fRank, tRank = 0, 0
    for data in datas:
      if(data[0] == mvFrom):
        fRank = data[1]
      if(data[0] == mvTo):
        tRank = data[1]
    self.updateType(mvFrom, tRank)
    for data in datas:
      if(fRank > tRank):
        if(data[1] < fRank and data[1] >= tRank):
          self.updateType(data[0], data[1]+1)
      else:
        if(data[1] > fRank and data[1] <= tRank):
          self.updateType(data[0], data[1]-1)
  # 获取Item数据
  def getItemData(self, url=None):
    if(url == None):
      query = 'SELECT * FROM ITEM ORDER BY RANK ASC'
      cursor = self.c.execute(query)
    else:
      query = 'SELECT * FROM ITEM WHERE URL=(?)'
      data = [url]
      cursor = self.c.execute(query, data)
    datas = []
    for cow in cursor:
      datas.append(cow)
    return datas
  # 根据类别获取Item数据
  def getItemDataFromType(self, type):
    query = 'SELECT * FROM ITEM WHERE TYPE=(?) ORDER BY RANK DESC'
    data = [type]
    cursor = self.c.execute(query, data)
    datas = []
    for cow in cursor:
      datas.append(cow)
    return datas
  # 更新Item
  def updateItem(self, url, type=None, title=None, rank=None, iconUrl=None, description=None, oldUrl=None):
    query, data = '', []
    if(oldUrl):# 若oldUrl不为空，修改数据
      if(type):
        query = '''UPDATE ITEM SET TYPE=(?) WHERE URL=(?)'''
        data = [type, oldUrl]
        self.c.execute(query, data)
      if(title):
        query = '''UPDATE ITEM SET TITLE=(?) WHERE URL=(?)'''
        data = [title, oldUrl]
        self.c.execute(query, data)
      if(rank):
        query = '''UPDATE ITEM SET RANK=(?) WHERE URL=(?)'''
        data = [rank, oldUrl]
        self.c.execute(query, data)
      if(iconUrl):
        query = '''UPDATE ITEM SET ICONURL=(?) WHERE URL=(?)'''
        data = [iconUrl, oldUrl]
        self.c.execute(query, data)
      if(description):
        query = '''UPDATE ITEM SET DESCRIPTION=(?) WHERE URL=(?)'''
        data = [description, oldUrl]
        self.c.execute(query, data)
      if(url):
        query = '''UPDATE ITEM SET URL=(?) WHERE URL=(?)'''
        data = [url, oldUrl]
        self.c.execute(query, data)
    else:# 若oldUrl为空
      datas = self.getItemData(url)
      if(len(datas) == 0):
        query = '''INSERT INTO ITEM (URL,TYPE,TITLE,RANK,ICONURL,DESCRIPTION) VALUES (?,?,?,?,?,?)'''
        data = [url, type, title, rank, iconUrl, description]
        self.c.execute(query, data)
      else:
        if(type):
          query = '''UPDATE ITEM SET TYPE=(?) WHERE URL=(?)'''
          data = [type, url]
          self.c.execute(query, data)
        if(title):
          query = '''UPDATE ITEM SET TITLE=(?) WHERE URL=(?)'''
          data = [title, url]
          self.c.execute(query, data)
        if(rank):
          query = '''UPDATE ITEM SET RANK=(?) WHERE URL=(?)'''
          data = [rank, url]
          self.c.execute(query, data)
        if(iconUrl):
          query = '''UPDATE ITEM SET ICONURL=(?) WHERE URL=(?)'''
          data = [iconUrl, url]
          self.c.execute(query, data)
        if(description):
          query = '''UPDATE ITEM SET DESCRIPTION=(?) WHERE URL=(?)'''
          data = [description, url]
          self.c.execute(query, data)
    self.conn.commit()
  # 删除Item
  def delItem(self, url):
    query = 'DELETE FROM ITEM WHERE URL=(?)'
    data = [url]
    self.c.execute(query, data)
    self.conn.commit()


# test code
if __name__ == '__main__':
  conn = sqlite3.connect('back-end/data/favourites.db')