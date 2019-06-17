# -*- coding: utf-8 -*-
'''Broker access module'''
import os
from datetime import datetime
from .common import get_dt_short, get_dt_long, n2d
from .const import ProductCode, HealthStatus, StateStatus, OrderSide, OrderType, OrderConditionType, OrderState
from .private import PrivateAPI
from .public import PublicAPI


class BrokerAPI(object):
    '''Broker access vlass'''

    class EventLog():   # pylint: disable=too-few-public-methods
        '''event log'''
        ORDER_BUY_MARKET = 'ORDER_BUY_MARKET'
        ORDER_BUY_LIMIT = 'ORDER_BUY_LIMIT'
        ORDER_SELL_MARKET = 'ORDER_SELL_MARKET'
        ORDER_SELL_LIMIT = 'ORDER_SELL_LIMIT'
        ORDER_CANCEL = 'ORDER_CANCEL'
        ORDER_ALL_CANCEL = 'ORDER_ALL_CANCEL'
        OCO_BUY_LIMIT_STOP = 'OCO_BUY_LIMIT_STOP'
        OCO_SELL_LIMIT_STOP = 'OCO_SELL_LIMIT_STOP'
        SPECIAL_ORDER_CANCEL = 'SPECIAL_ORDER_CANCEL'

    @staticmethod
    def str2dt(str_dt):
        '''Convert string to datetime type'''
        try:
            TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S'
            return datetime.strptime(str_dt[0:18], TIMESTAMP_FORMAT)
        except:
            return None

    @staticmethod
    def get_product_code():
        '''get product code'''
        return ProductCode.BTC_JPY

    def __init__(self, key, secret, log=True, *, get_timeout=None, post_timeout=None):
        """イニシャライザ"""
        self.broker_name = 'bitflyer'
        self.product_code = self.get_product_code()

        self.__api_key = key
        self.__api_secret = secret
        self.__get_timeout = get_timeout
        self.__post_timeout = post_timeout
        self._prv_api = PrivateAPI(self.__api_key, self.__api_secret,
                                   get_timeout=self.__get_timeout,
                                   post_timeout=self.__post_timeout)

        self.__log = log
        if self.__log:
            log_dir = './log/' + self.broker_name + '/'
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            self.__log_path = (log_dir
                               + get_dt_short()
                               + '_order'
                               + '_' + self.broker_name
                               + '_' + self.product_code
                               + '.csv')
            with open(self.__log_path, 'w') as flog:
                header_str = ('date time'
                              ',event'
                              ',order id'
                              ',price'
                              ',amount'
                              ',success'
                              ',facility'
                              '\n')
                flog.writelines(header_str)

    def __logging_event(self, event, order_id, price, anount, success, facility):
        '''イベント保存'''
        if self.__log:
            wstr = (get_dt_long() + ','
                    + str(event) + ','
                    + str(order_id) + ','
                    + str(price) + ','
                    + str(anount) + ','
                    + str(success) + ','
                    + str(facility) + '\n')

            with open(self.__log_path, 'a') as flog:
                flog.writelines(wstr)

    # -------------------------------------------------------------------------
    # Private API
    # -------------------------------------------------------------------------
    class AssetInfo:
        '''資産情報'''
        name = None
        onhand_amount = None
        free_amount = None

        @property
        def locked_amount(self):
            '''[property] locked amount'''
            if self.onhand_amount is None or self.free_amount is None:
                return None
            return self.onhand_amount - self.free_amount

    def get_assets(self):
        '''資産残高を取得'''
        result = False
        rtn_assets = {}
        try:
            res_balances = self._prv_api.get_getbalance()
            for blance in res_balances:
                asset_info = self.AssetInfo()
                asset_info.name = blance['currency_code']
                asset_info.onhand_amount = n2d(blance['amount'])
                asset_info.free_amount = n2d(blance['available'])
                rtn_assets[asset_info.name] = asset_info
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            rtn_assets = None
        return result, rtn_assets

    def order_check_detail(self, order_id):
        """注文状況の詳細を取得"""
        result = False
        rtn_order = None
        try:
            res_infos = self._prv_api.get_childorders(self.product_code, child_order_acceptance_id=order_id)
            if len(res_infos) > 0:  # pylint: disable-msg=C1801
                rtn_order = OrderInfo(res_infos[0])
                result = True
            else:
                result = True
                rtn_order = OrderInfo()
        except:     # pylint: disable-msg=W0702
            result = False
            rtn_order = None
        return result, rtn_order

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    def get_markets(self):
        '''マーケットの一覧取得'''
        result = False
        res_dct = None
        try:
            res_dct = PublicAPI(timeout=self.__get_timeout).get_markets()
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            res_dct = None
        return result, res_dct

    def get_depth_data(self):
        ''' 板情報の取得 '''
        result = False
        res_dct = None
        try:
            res_dct = PublicAPI(timeout=self.__get_timeout).get_depth(self.product_code)
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            res_dct = None
            import traceback
            with open('error_saapi.log', 'a') as f:
                f.write(dt.get_dt_long() + '\n')
                traceback.print_exc(file=f)
        return result, res_dct

    def get_ticker(self):
        '''Tickerの取得'''
        result = False
        res_dct = None
        try:
            res_dct = PublicAPI(timeout=self.__get_timeout).get_ticker(self.product_code)
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            res_dct = None
        return result, res_dct

    def get_executions(self):
        ''' 約定履歴の取得 '''
        result = False
        res_dct = None
        try:
            res_dct = PublicAPI(timeout=self.__get_timeout).get_executions(self.product_code)
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            res_dct = None
        return result, res_dct

    def get_depth_status(self):
        ''' 板の状態の取得 '''
        result = False
        health = HealthStatus.STOP
        state = StateStatus.CLOSED
        try:
            res_dct = PublicAPI(timeout=self.__get_timeout).get_boardstate(self.product_code)
            health = res_dct['health']
            state = es_dct['state']
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            health = HealthStatus.STOP
            state = StateStatus.CLOSED
        return result, health, state

    def get_broker_status(self):
        ''' 取引所の状態の取得 '''
        result = False
        health = HealthStatus.STOP
        try:
            res_dct = PublicAPI(timeout=self.__get_timeout).get_health(self.product_code)
            health = res_dct['status']
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            health = HealthStatus.STOP
        return result, health

    def get_chats(self):
        ''' チャットの取得 '''
        result = False
        res_dct = None
        try:
            res_dct = PublicAPI(timeout=self.__get_timeout).get_chats()
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            res_dct = None
        return result, res_dct

    # -------------------------------------------------------------------------
    # Private API
    # -------------------------------------------------------------------------
    def order_buy_limit(self, price, amount):
        '''指値買い注文を出す'''
        result = False
        order_id = None
        try:
            res_order = self._prv_api.send_childorder_limit_buy(self.product_code, float(price), float(amount))
            order_id = res_order['child_order_acceptance_id']
            result = True
        except:     # pylint: disable-msg=W0702
            order_id = None
            result = False

        self.__logging_event(self.EventLog.ORDER_BUY_LIMIT,
                             order_id,
                             price, amount,
                             result, '')

        return result, order_id

    def order_buy_market(self, amount):
        '''成行買い注文を出す'''
        result = False
        order_id = None
        try:
            res_order = self._prv_api.send_childorder_market_buy(self.product_code, float(amount))
            order_id = res_order['child_order_acceptance_id']
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            order_id = None

        self.__logging_event(self.EventLog.ORDER_BUY_MARKET,
                             order_id,
                             None, amount,
                             result, '')

        return result, order_id

    def order_sell_limit(self, price, amount):
        '''指値買い注文を出す'''
        result = False
        order_id = None
        try:
            res_order = self._prv_api.send_childorder_limit_sell(self.product_code, float(price), float(amount))
            order_id = res_order['child_order_acceptance_id']
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            order_id = None

        self.__logging_event(self.EventLog.ORDER_SELL_LIMIT,
                             order_id,
                             price, amount,
                             result, '')

        return result, order_id

    def order_sell_market(self, amount):
        '''成行売り注文を出す'''
        result = False
        order_id = None
        try:
            res_order = self._prv_api.send_childorder_market_sell(self.product_code, float(amount))
            order_id = res_order['child_order_acceptance_id']
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            order_id = None

        self.__logging_event(self.EventLog.ORDER_SELL_MARKET,
                             order_id,
                             None, amount,
                             result, '')

        return result, order_id

    def order_cancel(self, order_id):
        '''注文をキャンセルする'''
        result = False
        try:
            self._prv_api.send_cancelchildorder(self.product_code, child_order_acceptance_id=order_id)
            result = True
        except:     # pylint: disable-msg=W0702
            result = False

        self.__logging_event(self.EventLog.ORDER_CANCEL,
                             order_id,
                             None, None,
                             result, '')

        return result

    def order_all_cancel(self):
        '''全ての注文をキャンセルする'''
        result = False
        try:
            self._prv_api.send_cancelallchildorders(self.product_code)
            result = True
        except:     # pylint: disable-msg=W0702
            result = False

        self.__logging_event(self.EventLog.ORDER_ALL_CANCEL, None, None, None, result, '')
        return result

    def parent_aid_to_oid(self, acceptance_id):
        '''Get parent_order_id from parent_order_acceptance_id'''
        result = False
        rtn_id = None
        try:
            res_info = self._prv_api.get_parentorder(parent_order_acceptance_id=acceptance_id)
            rtn_id = res_info['parent_order_id']
            result = True
        except:
            result = False
            rtn_id = None

        return result, rtn_id

    def so_check_details(self, parent_order_id):
        '''check special order information'''
        result = False
        rtn_orders = None
        try:
            res_infos = self._prv_api.get_childorders(self.product_code, parent_order_id=parent_order_id)
            rtn_orders = []
            if len(res_infos) > 0:  # pylint: disable-msg=C1801
                for info in res_infos:
                    rtn_orders.append(OrderInfo(info))
                result = True
            else:
                result = True
                rtn_orders.append(OrderInfo())
        except:     # pylint: disable-msg=W0702
            result = False
            rtn_orders = None
        return result, rtn_orders

    def so_mk_prms_limit(self, product_code, side, price, size) -> dict:
        '''return parameters of dicttype parent order'''
        res_dict = {
            'product_code': product_code,
            'condition_type': OrderConditionType.LIMIT,
            'side': side,
            'price': price,
            'size': size
        }
        return res_dict

    def so_mk_prms_stop(self, product_code, side, price, size) -> dict:
        '''return parameters of dicttype parent order'''
        res_dict = {
            'product_code': product_code,
            'condition_type': OrderConditionType.STOP,
            'side': side,
            'trigger_price': price,
            'size': size
        }
        return res_dict

    def so_oco_buy_limit_stop(self, o_price, s_price, amount):
        '''oco type buying order of limit and trail'''
        result = False
        order_id = None
        try:
            # make order list
            prms_order = self.so_mk_prms_limit(self.product_code, OrderSide.BUY, float(o_price), float(amount))
            prms_stop = self.so_mk_prms_stop(self.product_code, OrderSide.BUY, float(s_price), float(amount))
            parameters = [prms_order, prms_stop]

            # send order
            res_order = self._prv_api.send_parentorder(OrderType.OCO, parameters)
            order_id = res_order['parent_order_acceptance_id']
            result = True
        except:
            result = False
            order_id = None

        self.__logging_event(self.EventLog.OCO_BUY_LIMIT_STOP,
                             order_id,
                             o_price, amount,
                             result, 'OCO1:LIMIT')
        self.__logging_event(self.EventLog.OCO_BUY_LIMIT_STOP,
                             order_id,
                             s_price, amount,
                             result, 'OCO2:STOP')

        return result, order_id

    def so_oco_sell_limit_stop(self, o_price, s_price, amount):
        '''oco type selling order of limit and trail'''
        result = False
        order_id = None
        try:
            # make order list
            prms_order = self.so_mk_prms_limit(self.product_code, OrderSide.SELL, float(o_price), float(amount))
            prms_stop = self.so_mk_prms_stop(self.product_code, OrderSide.SELL, float(s_price), float(amount))
            parameters = [prms_order, prms_stop]

            # send order
            res_order = self._prv_api.send_parentorder(OrderType.OCO, parameters)
            order_id = res_order['parent_order_acceptance_id']
            result = True
        except:
            result = False
            order_id = None

        self.__logging_event(self.EventLog.OCO_SELL_LIMIT_STOP,
                             order_id,
                             o_price, amount,
                             result, 'OCO1:LIMIT')
        self.__logging_event(self.EventLog.OCO_SELL_LIMIT_STOP,
                             order_id,
                             s_price, amount,
                             result, 'OCO2:STOP')

        return result, order_id

    def so_cancel(self, *, parent_order_acceptance_id=None, parent_order_id=None):
        '''cancel special order'''
        result = False
        memo = None
        c_id = None
        try:
            if parent_order_acceptance_id is not None:
                c_id = parent_order_acceptance_id
                memo = 'parent_order_acceptance_id'
                self._prv_api.send_cancelparentorder(
                    self.product_code, parent_order_acceptance_id=parent_order_acceptance_id)
                result = True

            elif parent_order_id is not None:
                c_id = parent_order_id
                memo = 'parent_order_id'
                self._prv_api.send_cancelparentorder(
                    self.product_code, parent_order_id=parent_order_id)
                result = True

            else:
                result = False

        except:     # pylint: disable-msg=W0702
            result = False

        self.__logging_event(self.EventLog.SPECIAL_ORDER_CANCEL, c_id, None, None, result, memo)
        return result


class OrderInfo(object):
    '''order information class'''
    order_id = None
    order_pair = None
    order_side = None
    order_type = None
    order_state = OrderState.UNKNOWN
    order_price = None
    order_amount = None
    executed_ave_price = None
    executed_amount = None
    executed_commission = None
    outstanding_amount = None
    canceled_amount = None
    expire_date = None
    order_date = None

    @property
    def executed_actual_amount(self):
        '''[property] actual amount'''
        if self.executed_amount is None or self.executed_commission is None:
            return None
        return self.executed_amount - self.executed_commission

    def __init__(self, info=None):
        if info is not None:
            self.order_id = info['child_order_acceptance_id']
            self.order_pair = info['product_code']
            self.order_side = info['side']
            self.order_type = info['child_order_type']
            self.order_price = n2d(info['price'])
            self.order_amount = n2d(info['size'])
            self.executed_ave_price = n2d(info['average_price'])
            self.executed_amount = n2d(info['executed_size'])
            self.executed_commission = n2d(info['total_commission'])
            self.outstanding_amount = n2d(info['outstanding_size'])
            self.canceled_amount = n2d(info['cancel_size'])
            self.expire_date = BrokerAPI.str2dt(info['expire_date'])
            self.order_date = BrokerAPI.str2dt(info['child_order_date'])
            self.order_state = info['child_order_state']

    def out_shell(self):
        '''Display information to shell'''
        print('order_id', self.order_id, type(self.order_id))
        print('order_pair', self.order_pair, type(self.order_pair))
        print('order_side', self.order_side, type(self.order_side))
        print('order_type', self.order_type, type(self.order_type))
        print('order_state', self.order_state, type(self.order_state))
        print('order_price', self.order_price, type(self.order_price))
        print('order_amount', self.order_amount, type(self.order_amount))
        print('executed_ave_price', self.executed_ave_price, type(self.executed_ave_price))
        print('executed_amount', self.executed_amount, type(self.executed_amount))
        print('executed_commission', self.executed_commission, type(self.executed_commission))
        print('executed_actual_amount', self.executed_actual_amount, type(self.executed_actual_amount))
        print('outstanding_amount', self.outstanding_amount, type(self.outstanding_amount))
        print('canceled_amount', self.canceled_amount, type(self.canceled_amount))
        print('expire_date', self.expire_date, type(self.expire_date))
        print('order_date', self.order_date, type(self.order_date))
