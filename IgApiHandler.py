import json
from requests import Session

class ApiHandler:
    def __init__(self, session: Session, api_key: str, environment: str):
        self.session = session
        self.API_KEY = api_key
        if str.lower(environment) == 'live':
            self.base_url = 'https://api.ig.com/gateway/deal'
        else:
            self.base_url = 'https://demo-api.ig.com/gateway/deal'
        self.session.headers.update({
            "X-IG-API-KEY": self.API_KEY,
            'Content-Type': 'application/json',
            'Accept': 'application/json; charset=UTF-8'
        })


    def make_url(self, endpoint: str):
        return self.base_url + endpoint


    def ensure_session(self, session: Session):
        if session == None:
            session = self.session
        else:
            session = session
        return session

    def prepare_call(self, endpoint: str, session: Session, version: str):
        url = self.make_url(endpoint)
        session = self.ensure_session(session)
        session.headers.update({'VERSION': version})
        return url, session
    

    def post(self, session: Session, endpoint: str, version: str, params: dict = None):
        url, session = self.prepare_session(endpoint, session, version)
        response = session.post(url, params = json.dumps(params))
        return response

    def get(self, session: Session, endpoint: str, version: str, params: dict = None):
        url, session = self.prepare_session(endpoint, session, version)
        response = session.get(url, params = json.dumps(params))
        return response

    def put(self, session: Session, endpoint: str, version: str, params: dict = None):
        url, session = self.prepare_session(endpoint, session, version)
        response = session.put(url, params = json.dumps(params))
        return response
    
    def delete(self, session: Session, endpoint: str, version: str, params: dict = None):
        url, session = self.prepare_session(endpoint, session, version)
        response = session.post(url, params = json.dumps(params))
        return response
