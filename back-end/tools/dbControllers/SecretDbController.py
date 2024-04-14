

class SecretDbController():
  # 初始化
  def __init__(self):
    try:
      file = open('datas/secret', 'r', encoding='utf-8')
      self.filepath = 'datas/secret'
    except:
      file = open('back-end/datas/secret', 'r', encoding='utf-8')
      self.filepath = 'back-end/datas/secret'
    self.data_list = []
    for line in file:
      datas = line.strip().split('::')
      data_item = {}
      data_item['date'] = datas[0]
      data_item['secret'] = '' if datas[1] == 'None' else datas[1]
      data_item['state'] = datas[2]
      data_item['message'] = '' if datas[3] == 'None' else datas[3]
      self.data_list.append(data_item)
    file.close()

  # 存储信息
  def save_data(self):
    file = open(self.filepath, 'w', encoding='utf-8')
    for data_item in self.data_list:
      if data_item['secret'] == '': data_item['secret'] = 'None'
      if data_item['message'] == '': data_item['message'] = 'None'
      file.write(data_item['date'] + '::' + data_item['secret'] + '::' + data_item['state'] + '::' + data_item['message'] + '\n')
    file.close()

  # 更新状态
  def updateState(self, date, state=None, message=None):
    for data_item in self.data_list:
      if data_item['date'] == date:
        if state != None: data_item['state'] = str(state)
        if message != None: data_item['message'] = message
        print(data_item)
    self.save_data()

  # 获取type数据，若title为空，返回所有
  def getSecret(self, date=None):
    return_data = {'date': date, 'secret': '', 'state': '-1', 'message': ''}
    if date:
      for data_item in self.data_list:
        if data_item['date'] == date:
          return data_item
    return return_data

# test code
if __name__ == '__main__':
  db = SecretDbController()
  print(db.getSecret('20240416'))
  db.updateState('20240416', 1, '你好')
  print(db.getSecret('20240416'))