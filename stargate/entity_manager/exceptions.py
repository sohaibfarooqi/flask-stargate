
class ApplicationError(AttributeError, IndexError):

	def __init__(self, message, elem, *args):

		self.element = elem
		self.message = message
		super(ApplicationError, self).__init__(self.message, self.element, *args)

class ColumnNotFoundException(ApplicationError):
	
	def __init__(self, column, message = None, *args):
		
		self.message = "ColumnNotFoundException: Unknown column %s" % column
		
		if message is not None:
			self.message = message

		super(ColumnNotFoundException, self).__init__(self.message, column, *args)	

class ColumnOperatorNotFoundException(ApplicationError):

	def __init__(self, op, message = None, *args):
		
		self.message = "ColumnOperatorNotFoundException: Unknown column operator %s" % op
		
		if message is not None:
			self.message = message
				
		super(OperatorNotFoundException, self).__init__(self.message, op, *args)

class LogicalOperatorNotFound(ApplicationError):
	
	def __init__(self, op, message = None, *args):
		
		self.message = "LogicalOperatorNotFound: No logical boolean operator found in statement:  %s" % op
		
		if message is not None:
			self.message = message
				
		super(LogicalOperatorNotFound, self).__init__(self.message, op, *args)	

class ParseException(ApplicationError):
	
	def __init__(self, expr, message = None, *args):
		
		self.message = "ParseException: Cannot Parse Expression Near:  %s" % expr
		
		if message is not None:
			self.message = message
				
		super(ParseException, self).__init__(self.message, expr, *args)	

class AmbiguousExpressionException(ApplicationError):

	def __init__(self, expr, message = None, *args):
		
		self.message = "AmbiguousExpressionException: Expression is Ambiguous Near:  %s" % expr
		
		if message is not None:
			self.message = message
				
		super(AmbiguousExpressionException, self).__init__(self.message, expr, *args)	