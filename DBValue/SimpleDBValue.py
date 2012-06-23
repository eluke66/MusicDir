from DBValue import DBValue

# Simple matching DB class.
class SimpleDBValue(DBValue):
  def __init__(self,value,table,col):
    self.value = value
    self.table = table
    self.col = col

  def __str__(self):
    return "%s.%s = %s" % (self.col,self.table,self.value)

  def emitSQL(self):
    sql = "%s.%s=?" % (self.table,self.col)
    vals = [self.value]
    return [sql,vals]

  # Input: None
  # Output: List of tables required by this item.
  def getTableList(self):
    return [self.table] 
