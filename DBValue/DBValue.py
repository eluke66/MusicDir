class DBValue:

  # Input: None
  # Output: A list containing two values:
  #   1. The string SQL statement
  #   2. A list of values to be passed to execute
  def emitSQL(self):
    raise Exception("DBValue::emitSQL not implemented!")

  # Input: None
  # Output: List of tables required by this item.
  def getTableList(self):
	  return []
