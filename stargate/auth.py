from .models import Auth, User
from flask import current_app as app
from sqlalchemy import and_
import datetime
from .extentions import db
import hashlib

class Authorization():
	
	def authorize_request(headers):
		
		if 'Auth-Token' in headers:
			auth_token = headers['Auth-Token']
			authorize = Auth.query.filter(Auth.auth_token == auth_token).first()
			
			if authorize is None:
				return False
			
			else:
				if authorize.remaining_time > 0:
					return True
				
				else:
					return False
		else:
			return False

	def login_user(username, password, headers):
		user = User.query.filter(and_(User.username == username), User.password == password).first()
		if user is None:
			return None
		else:
			return Authorization.__registerAuthDetails(headers, user)
			
	def __registerAuthDetails(headers, user):
		auth_object = Auth()
		
		auth_object.auth_token = Authorization.__generateAuthToken(user.username + user.password)
		auth_object.user_agent = headers['User-Agent']
		auth_object.ip_address = headers['Host']
		auth_object.created_at = datetime.datetime.now()
		auth_object.updated_at = auth_object.created_at
		auth_object.expires_at = auth_object.created_at + datetime.timedelta(minutes=app.config['TOKEN_EXPIRATION'])
		auth_object.user_id    = user.id

		db.session.add(auth_object)
		db.session.commit()
		return auth_object

	def __generateAuthToken(user_info):
		user_info = user_info.encode('utf-8')
		secret_key = app.config['SECRET_KEY'].encode('utf-8')
		return hashlib.sha256(user_info + secret_key).hexdigest()
