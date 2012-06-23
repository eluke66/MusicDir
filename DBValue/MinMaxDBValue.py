from DBValue import DBValue

# Min/max matching DB class.
class MinMaxDBValue(DBValue):
  def __init__(self,min,max,table,col):
    self.min = min
    self.max = max
    self.table = table
    self.col = col

  def __str__(self):
    return "%d < %s.%s < %d" % (self.min,self.table,self.col,self.max)

  def emitSQL(self):
    tag = "%s.%s" % (self.table,self.col)
    sql = "%s >= ? AND %s <= ?" % (tag,tag)
    vals = [self.min, self.max]
    return [sql,vals]

  # Input: None
  # Output: List of tables required by this item.
  def getTableList(self):
    return [self.table] 
