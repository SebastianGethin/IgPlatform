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


    def ensure_session(self, session: Session = None):
        if session == None:
            session = self.session
        else:
            session = session
        return session
    

    def post(self, session: Session, endpoint: str, version: str, params: dict = None):
        url = self.make_url(endpoint)
        session = self.ensure_session(session)
        session.headers.update({'VERSION': version})
        response = session.post(url, json.dumps(params))
        return response

    def get(self, session: Session, endpoint: str, version: str, params: dict = None):
        url = self.make_url(endpoint)
        session = self.ensure_session(session)
        session.headers.update({'VERSION': version})
        response = session.get(url, params = json.dumps(params))
        return response

    def put(self, session: Session, endpoint: str, version: str, params: dict = None):
        url = self.make_url(endpoint)
        session = self.ensure_session(session)
        session.headers.update({'VERSION': version})
        response = session.put(url, json.dumps(params))
        return response
    
    def delete(self, session: Session, endpoint: str, version: str, params: dict = None):
        url = self.make_url(endpoint)
        session = self.ensure_session(session)
        session.headers.update({'VERSION': version})
        response = session.post(url, json.dumps(params))
        return response

    # def callApi(self, operation: Session.function, session: Session, endpoint: str, version: str, params: dict):
        
    #     url = self.make_url(endpoint)
    #     session = self.ensure_session(session)
    #     session.headers.update({'VERSION': version})
    #     response = operation(url, json.dumps(params))