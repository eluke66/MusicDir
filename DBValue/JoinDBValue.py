from DBValue import DBValue

# DB class used to join two tables
# colA.tableA = colB.tableB
class JoinDBValue(DBValue):
  def __init__(self,colA,tableA,colB,tableB):
    self.colA = colA
    self.tableA = tableA
    self.colB = colB
    self.tableB = tableB

  def __str__(self):
    return "%s.%s = %s.%s" % (self.tableA,self.colA, self.tableB, self.colB)

  def emitSQL(self):
    sql = "%s.%s=%s.%s" %(self.tableA,self.colA, self.tableB, self.colB)
    vals = []
    return [sql,vals]

  # Input: None
  # Output: List of tables required by this item.
  def getTableList(self):
    return [self.tableA,self.tableB] 
