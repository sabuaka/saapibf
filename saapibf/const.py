# -*- coding: utf-8 -*-
'''const value'''

# pylint: disable=too-few-public-methods


class Asset():
    '''asset'''
    LTC = 'LTC'
    BCH = 'BCH'
    BTC = 'BCH'
    MONA = 'MONA'
    LSK = 'LSK'
    ETC = 'ETC'
    JPY = 'JPY'
    ETH = 'ETH'


class ProductCode():
    '''product code'''
    BTC_JPY = 'BTC_JPY'
    FX_BTC_JPY = 'FX_BTC_JPY'


class HealthStatus():
    '''health status'''
    NORMAL = 'NORMAL'           # 取引所は稼動しています。
    BUSY = 'BUSY'               # 取引所に負荷がかかっている状態です。
    VERY_BUSY = 'VERY BUSY'     # 取引所の負荷が大きい状態です。
    SUPER_BUSY = 'SUPER BUSY'   # 負荷が非常に大きい状態です。発注は失敗するか、遅れて処理される可能性があります。
    NO_ORDER = 'NO ORDER'       # 発注が受付できない状態です。
    STOP = 'STOP'               # 取引所は停止しています。発注は受付されません。


class StateStatus():
    '''state status'''
    RUNNING = 'RUNNING'                 # 通常稼働中
    CLOSED = 'CLOSED'                   # 取引停止中
    STARTING = 'STARTING'               # 再起動中
    PREOPEN = 'PREOPEN'                 # 板寄せ中
    CIRCUIT_BREAK = 'CIRCUIT BREAK'     # サーキットブレイク発動中
    AWAITING_SQ = 'AWAITING SQ'         # LightningFuturesの取引終了後SQ（清算値）の確定前
    MATURED = 'MATURED'                 # LightningFuturesの満期に到達


class OrderSide():
    '''trade side'''
    BUY = 'BUY'
    SELL = 'SELL'


class OrderType():
    '''order type'''
    # normal order
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    # special order
    SIMPLE = 'SIMPLE'
    IFD = 'IFD'
    OCO = 'OCO'
    IFDOCO = 'IFDOCO'


class OrderConditionType():
    '''特殊注文の執行条件'''
    LIMIT = 'LIMIT'             # Limit order.
    MARKET = 'MARKET'           # Market order.
    STOP = 'STOP'               # Stop order.
    STOP_LIMIT = 'STOP_LIMIT'   # Stop-limit order.
    TRAIL = 'TRAIL'             # Trailing stop order.
