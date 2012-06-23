from DBValue import DBValue


# Multi matching DB class.
class MultiDBValue(DBValue):
  def __init__(self,vals,table,col):
    self.vals = vals
    self.table = table
    self.col = col

  def __str__(self): 
    valStr = str(self.vals)
    return "%s.%s = %s" % (self.table,self.col,valStr)

  def emitSQL(self):
    sql = "("
    tag = "%s.%s" % (self.table,self.col)

    for item in self.vals:
      sql += "%s=? OR " % (tag)

    # Pull off the last "OR"
    sql = sql[0:sql.rfind("OR")-1] + ")"
    vals = self.vals
    return [sql,vals]
   

  # Input: None
  # Output: List of tables required by this item.
  def getTableList(self):
    return [self.table] 
