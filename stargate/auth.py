from .models import Auth, User
from flask import current_app as app
from sqlalchemy import and_
import datetime
from .extentions import db
import hashlib

class Authorization():
	
	def authorize_request(headers):
		auth_token = headers['Authorization']
		authorize = Auth.query.filter(Auth.auth_token == auth_token).first()
		
		if authorize is None:
			if Authorization.__login(headers):
				return True
			else:
				return False
		
		else:
			if authorize.remaining_time <= 0:
				return True
			
			else:
				return False

	def __login(headers):
		auth_token = headers['Authorization']
		data = auth_token.split(':')
		user = User.query.filter(and_(User.username == data[0]), User.password == data[1]).first()
		if user is None:
			return False
		else:
			Authorization.__registerAuthDetails(headers, user)
			return True

	def __registerAuthDetails(headers, user):
		auth_object = Auth()
		
		auth_object.auth_token = Authorization.__generateAuthToken(headers['Authorization'])
		auth_object.user_agent = headers['User-Agent']
		auth_object.ip_address = headers['Host']
		auth_object.created_at = datetime.datetime.now()
		auth_object.updated_at = auth_object.created_at
		auth_object.expires_at = auth_object.created_at + datetime.timedelta(minutes=app.config['AUTH_EXPIRY'])
		auth_object.user_id    = user.id

		db.session.add(auth_object)
		db.session.commit()
		return True

	def __generateAuthToken(user_info):
		user_info = user_info.encode('utf-8')
		secret_key = app.config['SECRET_KEY'].encode('utf-8')
		return hashlib.md5(user_info + secret_key).hexdigest()
