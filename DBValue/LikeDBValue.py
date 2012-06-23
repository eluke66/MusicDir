from DBValue import DBValue

# Like matching DB class.
class LikeDBValue(DBValue):
  def __init__(self,value,table,col):
    self.value = value
    self.table = table
    self.col = col

  def __str__(self):
    return "%s.%s is like %s" % (self.table,self.col,self.value)

  def emitSQL(self):
    sql = "%s.%s LIKE ?" % (self.table,self.col)
    vals = [self.value]
    return [sql,vals]

  # Input: None
  # Output: List of tables required by this item.
  def getTableList(self):
    return [self.table] 
