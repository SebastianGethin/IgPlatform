import pandas as pd
import trading_ig_config
import IgApiHandler
from datetime import datetime
from requests import Session, Response
import json
from decimal import Decimal

# exception handling class, for when the IG API returns an unsuccessful response code
class IGException(Exception):
    print('IG has raised an exception')
    pass



# base class for establishing a connection to the IG service
class IGREST:
    def __init__(self, session: Session = None):
        self.config = trading_ig_config.api_config()
        self.CST = None
        self.XST = None
        if session is None:
            self.session = Session()
        else:
            self.session = session
        self.api_handler = IgApiHandler.ApiHandler(self.session, self.config.api_key, self.config.acc_type)
        
    def create_session(self, session: Session = None):
        session = self.api_handler.ensure_session(session)
        version = '2'
        endpoint = '/session',
        params = {'identifier': self.config.username,
                  'password': self.config.password}
        response = self.api_handler.post(session = self.session, version = version, endpoint = endpoint, params = params)
        if response.status_code == 200:
            self.set_security_headers(response, self.session)
        else:
            raise IGException(response.text)

    def set_security_headers(self, response: Response, session: Session):
        if 'CST' in response.headers:
            session.headers.update({'CST': response.headers['CST']})
            print('cst set')
        if 'X-SECURITY-TOKEN' in response.headers:
            session.headers.update({'X-SECURITY-TOKEN': response.headers['X-SECURITY-TOKEN']})
            print('X Security Token set')



# class for pulling data from the IG APIs. Data is returned in pandas dataframes
class IGMarketData(IGREST):
    def get_historical_data_daterange(self, epic: str, resolution: str, start_date: datetime, end_date: datetime = datetime.now(), session: Session = None):
        version = '2'
        endpoint = '/prices/{epic}/{resolution}/{start_date}/{end_date}'.format(epic = epic, resolution = resolution, start_date = start_date, end_date = end_date)
        response = self.api_handler.get(session = session, version = version, endpoint = endpoint)
        data = json.loads(response.text)
        if response.status_code == 200:
            return self.prices_as_dataframe(data['prices'])
        else:
            raise IGException(data)
    
    def get_historical_data_numpoints(self, epic: str, resolution: str, numpoints: int, session: Session = None):
        version = '2'
        endpoint = '/prices/{epic}/{resolution}/{numpoints}'.format(epic = epic, resolution = resolution, numpoints = numpoints)
        response = self.api_handler.get(session = session, version = version, endpoint = endpoint)
        data = json.loads(response.text)
        if response.status_code == 200:
            return self.prices_as_dataframe(data['prices'])
        else:
            raise IGException(data)

    def prices_as_dataframe(self, data: json):
        df = pd.json_normalize(data)
        df = df.set_index('snapshotTime')
        df.index = pd.to_datetime(df.index)
        df.index.name = "DateTime"
        df.drop(columns = ['openPrice.lastTraded',
                           'highPrice.lastTraded',
                           'lowPrice.lastTraded',
                           'closePrice.lastTraded'], inplace = True)
        df.rename(columns = {'openPrice.ask': 'open_ask',
                             'openPrice.bid': 'open_bid',
                             'highPrice.ask': 'high_ask',
                             'highPrice.bid': 'high_bid',
                             'lowPrice.ask': 'low_ask',
                             'lowPrice.bid': 'low_bid',
                             'closePrice.ask': 'close_ask',
                             'closePrice.bid': 'close_bid',
                             'lastTradedVolume': 'volume'}, inplace = True)
        return df
    
    def market_navigation(self, session: Session = None):
        version = '1'
        endpoint = '/marketnavigation'
        response = self.api_handler.get(session = session, version = version, endpoint = endpoint)
        data = json.loads(response.text)
        if response.status_code == 200:
            if data['nodes'] is None:
                data['nodes'] = pd.DataFrame(columns = ['id', 'name'])
            else:
                data['nodes'] = pd.json_normalize(data['nodes'])
            if data['markets'] is None:
                data['markets'] = pd.DataFrame(columns = [  "bid",
                                                            "delayTime",
                                                            "epic",
                                                            "expiry",
                                                            "high",
                                                            "instrumentName",
                                                            "instrumentType",
                                                            "lotSize",
                                                            "low",
                                                            "marketStatus",
                                                            "netChange",
                                                            "offer",
                                                            "otcTradeable",
                                                            "percentageChange",
                                                            "scalingFactor",
                                                            "streamingPricesAvailable",
                                                            "updateTime"])
            else:
                data['markets'] = pd.json_normalize(data['markets'])
                return {'nodes': data['nodes'],
                    'markets': data['markets']}
        else:
            raise IGException(data)
    
    def market_node(self, nodeId: str, session: Session = None):
        version = '1'
        endpoint = '/marketnavigation/{nodeId}'.format(nodeId = nodeId)
        response = self.api_handler.get(session = session, version = version, endpoint = endpoint)
        data = json.loads(response.text)
        if response.status_code == 200:
            if data['nodes'] is None:
                data['nodes'] = pd.DataFrame(columns = ['id', 'name'])
            else:
                data['nodes'] = pd.json_normalize(data['nodes'])
            if data['markets'] is None:
                data['markets'] = pd.DataFrame(columns = [  "bid",
                                                            "delayTime",
                                                            "epic",
                                                            "expiry",
                                                            "high",
                                                            "instrumentName",
                                                            "instrumentType",
                                                            "lotSize",
                                                            "low",
                                                            "marketStatus",
                                                            "netChange",
                                                            "offer",
                                                            "otcTradeable",
                                                            "percentageChange",
                                                            "scalingFactor",
                                                            "streamingPricesAvailable",
                                                            "updateTime"])
            else:
                data['markets'] = pd.json_normalize(data['markets'])
            return data
        else:
            raise IGException(data)

    def market_details(self, epics: str, filter: str = 'ALL', session: Session = None):
        version = '2'
        endpoint = '/markets'
        params = {'epics': epics,
                  'filter': filter}
        response = self.api_handler.get(session = session, version = version, endpoint = endpoint, params = params)
        if response.status_code == 200:    
            return json.loads(response.text)
        else:
            raise IGException(response.text)

    def search_markets(self, searchTerm: str, session: Session = None):
        version = '1'
        endpoint = '/markets?searchTerm={searchTerm}'.format(searchTerm = searchTerm)
        response = self.api_handler.get(session = session, version = version, endpoint = endpoint)
        data = json.loads(response.text)
        if response.status_code == 200:
            return pd.json_normalize(data['markets'])
        else:
            raise IGException(data)



# class for interacting with the IG account, for reading transaction history, account balances, etc
class IGAccountData(IGREST):
    def list_accounts(self, session: Session = None):
        version = '1'
        endpoint = '/accounts'
        response = self.api_handler.get(session = session, version = version, endpoint = endpoint)
        data = json.loads(response.text)
        if response.status_code == 200:
            accounts = pd.json_normalize(data['accounts'])
            accounts.rename(columns={'balance.balance': 'balance',
                                     'balance.deposit': 'deposit',
                                     'balance.profitLoss': 'profitLoss',
                                     'balance.available': 'availableBalance'}, inplace=True)
            return accounts
        else:
            raise IGException(data)
    
    def account_preferences(self, session: Session = None):
        version = '1'
        endpoint = '/accounts/preferences'
        response = self.api_handler.get(session = session, version = version, endpoint = endpoint)
        preference = json.loads(response.text)
        if response.status_code == 200:
            return dict(preference)
        else:
            raise IGException(preference)
    
    def update_account_preferences(self, trailingStopsEnabled: str = 'false', session: Session = None):
        version = '1'
        endpoint = '/accounts/preferences'
        params = {'trailingStopsEnabled': trailingStopsEnabled}
        response = self.api_handler.put(session = session, version = version, endpoint = endpoint, params = params)
        data = dict(json.loads(response.text))
        if response.status_code == 200:
            return data
        else:
            raise IGException(data)

    def account_history(self, maxSpanSeconds: int, pageSize: int, dateFrom: datetime, dateTo: datetime = datetime.now(), session: Session = None):
        version = '2'
        endpoint = '/history/activity'
        params = {'from': dateFrom,
                  'to': dateTo,
                  'maxSpanSeconds': maxSpanSeconds,
                  'pageSize': pageSize,
                  'pageNumber': 1}
        has_more = True
        history = []
        while has_more:
            response = self.api_handler.get(session = session, endpoint = endpoint, version = version, params = params)
            data = json.loads(response.text)
            if response.status_code == 200:
                history.extend(data['activities'])
                if data['metadata']['pageData']['totalPages'] == 0 or data['metadata']['pageData']['pageNumber'] == data['metadata']['pageData']['totalPages']:
                    has_more = False
                else:
                    params['pageNumber'] += 1
            else:
                raise IGException(data)
        history = pd.DataFrame(history)
        return history
        
    
    def transaction_history(self, maxSpanSeconds: int, pageSize: int, dateFrom: datetime, dateTo: datetime = datetime.now(), transactionType: str = 'ALL', session: Session = None):
        version = '2'
        endpoint = '/history/transactions'
        params = {'transactionType': transactionType,
                  'from': dateFrom,
                  'to': dateTo,
                  'maxSpanSeconds': maxSpanSeconds,
                  'pageSize': pageSize,
                  'pageNumber': 1}
        has_more = True
        history = []
        while has_more:
            response = self.api_handler.get(session = session, endpoint = endpoint, version = version, params = params)
            data = json.loads(response.text)
            if response.status_code == 200:
                history.extend(data['transactions'])
                if data['metadata']['pageData']['totalPages'] == 0 or data['metadata']['pageData']['pageNumber'] == data['metadata']['pageData']['totalPages']:
                    has_more = False
                else:
                    params['pageNumber'] += 1
            else:
                raise IGException(data)
        return pd.DataFrame(history)

    def list_watchlists(self, session: Session = None):
        version = '1'
        endpoint = '/watchlists'
        response = self.api_handler.get(session = session, version = version, endpoint = endpoint)
        data = json.loads(response)['watchlists']
        if response.status_code == 200:
            return pd.json_normalize(data)
        else:
            raise IGException(data)
    
    def create_watchlist(self, name: str, epics: list, session: Session = None):
        version = '1'
        endpoint = '/watchlists'
        params = {'name': name,
                  'epics': epics}
        response = self.api_handler.post(session = session, version = version, endpoint = endpoint, params = params)
        data = json.loads(response.text)
        if response.status_code == 200:
            return data
        else:
            raise IGException(data)

    def add_to_watchlist(self, watchlistId: str, epic: str, session: Session = None):
        version = '1'
        endpoint = '/watchlists/{watchlistId}'.format(watchlistId = watchlistId)
        params = {'epic': epic}
        response = self.api_handler.put(session = session, version = version, endpoint = endpoint, params = params)
        data = json.loads(response.text)
        if response.status_code == 200:
            return data['status']
        else:
            raise IGException(data)
    
    def remove_from_watchlist(self, watchlistId: str, epic: str, session: Session = None):
        version = '1'
        endpoint = '/watchlists/{watchlistId}/{epic}'.format(watchlistId = watchlistId, epic = epic)
        response = self.api_handler.delete(session = session, version = version, endpoint = endpoint)
        data = json.loads(response.text)
        if response.status_code == 200:
            return data['status']
        else:
            raise IGException(data)

    def get_watchlist(self, watchlistId: str, session: Session = None):
        version = '1'
        endpoint = '/watchlists/{watchlistId}'.format(watchlistId = watchlistId)
        response = self.api_handler.get(session = session, version = version, endpoint = endpoint)
        data = json.loads(response.text)
        if response.status_code == 200:
            return pd.json_normalize(data['markets'])
        else:
            raise IGException(data)
        
    def delete_watchlist(self, watchlistId: str, session: Session = None):
        version = '1'
        endpoint = '/watchlists/{watchlistId}'.format(watchlistId = watchlistId)
        response = self.api_handler.delete(session = session, version = version, endpoint = endpoint)
        data = json.loads(response.text)
        if response.status_code == 200:
            return data['status']
        else:
            raise IGException(data)        



# class for placing orders and opening positions on the IG markets, as well as altering, deleting and closing them
class IGDealer(IGAccountData):
    def open_position(self, currencyCode: str, direction: str, epic: str, level: Decimal, orderType: str, size: Decimal, expiry: str = None, forceOpen: bool = False, guaranteedStop: bool = False, limitDistance: Decimal = None, limitLevel: Decimal = None, quoteId: str = None, stopDistance: Decimal = None, stopLevel: Decimal = None, timeInForce: str = None, trailingStop: Decimal = None, trailingStopIncrement: int = None, dealReference: str = datetime.now().strftime(format = '%Y/%m/%d %H:%M:%S'), session: Session = None):
        version = '2'
        endpoint = '/positions/otc'
        params = {'currencyCode': currencyCode,
                  'dealReference': dealReference,
                  'direction': direction,
                  'epic': epic,
                  'expiry': expiry,
                  'forceOpen': forceOpen,
                  'guaranteedStop': guaranteedStop,
                  'level': level,
                  'limitDistance': limitDistance,
                  'limitLevel': limitLevel,
                  'orderType': orderType,
                  'quoteId': quoteId,
                  'size': size,
                  'stopDistance': stopDistance,
                  'stopLevel': stopLevel,
                  'timeInForce': timeInForce,
                  'trailingStop': trailingStop,
                  'trailingStopIncrement': trailingStopIncrement}
        response = self.api_handler.post(session = session, version = version, endpoint = endpoint, params = params)
        deal = json.loads(response.text)
        if response.status_code == 200:
            return self.get_deal_confirmation(dealId = deal['dealReference'])
        else:
            raise IGException(deal)
    
    def close_position(self, dealId: str, direction: str, epic: str, expiry: str, level: Decimal, orderType: str, size: Decimal, timeInForce: str, quoteId: str = None, session: Session = None):
        version = '1'
        endpoint = '/positions/otc'
        params = {'dealId': dealId,
                  'direction': direction,
                  'epic': epic,
                  'expiry': expiry,
                  'level': level,
                  'orderType': orderType,
                  'quoteId': quoteId,
                  'size': size,
                  'timeInForce': timeInForce}
        response = self.api_handler.delete(session = session, version = version, endpoint = endpoint, params = params)
        deal = json.loads(response.text)
        if response.status_code == 200:
            return self.get_deal_confirmation(dealId = deal['dealReference'])
        else:
            raise IGException(deal)
    
    def update_position(self, dealId: str, guaranteedStop: bool = False, limitLevel: Decimal = None, stopLevel: Decimal = None, trailingStop: bool = False, trailingStopDistance: Decimal = None, trailingStopIncrement: Decimal = None, session: Session = None):
        version = '2'
        endpoint = '/positions/otc/{dealId}'.format(dealId = dealId)
        params = {'guaranteedStop': guaranteedStop,
                  'limitLevel': limitLevel,
                  'stopLevel': stopLevel,
                  'trailingStop': trailingStop,
                  'trailingStopDistance': trailingStopDistance,
                  'trailingStopIncrement': trailingStopIncrement}
        response = self.api_handler.put(session = session, version = version, endpoint = endpoint, params = params)
        deal = json.loads(response.text)
        if response.status_code == 200:
            return self.get_deal_confirmation(dealId = deal['dealReference'])
        else:
            raise IGException(deal)
    
    def list_positions(self, session: Session = None):
        version = '2'
        endpoint = '/positions'
        response = self.api_handler.get(session = session, version = version, endpoint = endpoint)
        data = json.loads(response.text)
        if response.status_code == 200:
            markets = pd.json_normalize(data['positions']['market'])
            positions = pd.json_normalize(data['positions']['position'])
            return (markets, positions)
        else:
            raise IGException(data)
    
    def list_working_orders(self, session: Session = None):
        version = '2'
        endpoint = '/workingorders'
        response = self.api_handler.get(session = session, version = version, endpoint = endpoint)
        data = json.loads(response.text)
        if response.status_code == 200:
            marketData = pd.json_normalize(data['workingOrders']['marketData'])
            workingOrderData = pd.json_normalize(data['workingOrders']['workingOrderData'])
            return (marketData, workingOrderData)
        else:
            raise IGException(data)

    def create_working_order(self, currencyCode: str, dealReference: str, direction: str, epic: str, expiry: str, forceOpen: bool, goodTillDate: datetime, guaranteedStop: str, level: Decimal, limitDistance: Decimal, limitLevel: Decimal, size: Decimal, stopDistance: Decimal, stopLevel: Decimal, timeInForce: str, type: str, session: Session = None):
        version = '2'
        endpoint = '/workingorders/otc'
        params = {'currencyCode': currencyCode,
                  'dealReference': dealReference,
                  'direction': direction,
                  'epic': epic,
                  'expiry': expiry,
                  'forceOpen': forceOpen,
                  'goodTillDate': goodTillDate,
                  'guaranteedStop': guaranteedStop,
                  'level': level,
                  'limitDistance': limitDistance,
                  'limitLevel': limitLevel,
                  'type': type,
                  'size': size,
                  'stopDistance': stopDistance,
                  'stopLevel': stopLevel,
                  'timeInForce': timeInForce}
        response = self.api_handler.post(session = session, version = version, endpoint = endpoint, params = params)
        deal = json.loads(response.text)
        if response.status_code == 200:
            return self.get_deal_confirmation(dealId = deal['dealReference'])
        else:
            raise IGException(deal)
    
    def delete_working_order(self, dealId: str, session: Session = None):
        version = '2'
        endpoint = '/workingorders/otc/{dealId}'.format(dealId = dealId)
        response = self.api_handler.delete(session = session, version = version, endpoint = endpoint)
        deal = json.loads(response.text)
        if response.status_code == 200:
            return self.get_deal_confirmation(dealId = deal['dealReference'])
        else:
            raise IGException(deal)

    def update_working_order(self, goodTillDate: datetime, guaranteedStop: bool, level: Decimal, limitDistance: Decimal, limitLevel: Decimal, stopDistance: Decimal, stopLevel: Decimal, timeInForce: str, type: str, session: Session = None):
        version = '2'
        endpoint = '/workingorders/otc'
        params = {'goodTillDate': goodTillDate,
                  'guaranteedStop': guaranteedStop,
                  'level': level,
                  'limitDistance': limitDistance,
                  'limitLevel': limitLevel,
                  'type': type,
                  'stopDistance': stopDistance,
                  'stopLevel': stopLevel,
                  'timeInForce': timeInForce}
        response = self.api_handler.post(session = session, version = version, endpoint = endpoint, params = params)
        deal = json.loads(response.text)
        if response.status_code == 200:
            return self.get_deal_confirmation(dealId = deal['dealReference'])
        else:
            raise IGException(deal)
    
    def open_sprint_market_position(self, dealReference: str, direction: str, epic: str, expiryPeriod: str, size: Decimal, session: Session = None):
        version = '1'
        endpoint = '/positions/sprintmarkets'
        params = {'dealReference': dealReference,
                  'direction': direction,
                  'epic': epic,
                  'expiryPeriod': expiryPeriod,
                  'size': size}
        response = self.api_handler.post(session = session, version = version, endpoint = endpoint, params = params)
        deal = json.loads(response.text)
        if response.status_code == 200:
            return self.get_deal_confirmation(dealId = deal['dealReference'])
        else:
            raise IGException(deal)
    
    def list_sprint_market_positions(self, session: Session = None):
        version = '2'
        endpoint = '/positions/sprintmarkets'
        response = self.api_handler.get(session = session, version = version, endpoint = endpoint)
        data = json.loads(response.text)
        if response.status_code == 200:
            return pd.json_normalize(data['sprintMarketPositions'])
        else:
            raise IGException(data)

    def get_deal_confirmation(self, dealId: str, session: Session = None):
        version = '2'
        endpoint = '/confirms/{dealId}'.format(dealId = dealId)
        response = self.api_handler.get(session = session, version = version, endpoint = endpoint)
        data = json.loads(response.text)
        if response.status_code == 200:
            return pd.json_normalize(data)
        else:
            raise IGException(data)