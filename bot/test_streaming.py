import pytest
import asyncio
from unittest.mock import MagicMock
from live_streamer import (
    is_sideways_market,
    read_alert,
    check_trade_status,
    trigger,
    monitor_symbol,
    monitor_symbols,
)

import logging

@pytest.mark.asyncio
async def test_is_sideways_market():
    # Mock DataFrame with necessary columns
    df_mock = MagicMock()
    df_mock.iloc.return_value = MagicMock()
    df_mock.iloc.return_value.__getitem__.side_effect = lambda x: {
        'upper_band': 1.0,
        'lower_band': 0.5,
        'close': 0.75,
    }.get(x)

    num_periods = 20
    market_condition, close_price = await is_sideways_market(df_mock, num_periods)
    assert market_condition == 'Hold'
    assert close_price == 0.75


def test_read_alert(tmp_path):
    log_file = tmp_path / "finish_trade.log"
    with open(log_file, 'w') as f:
        f.write("XRPUSDT, 0.75, Long\n")

    is_empty, data = read_alert(log_file)
    assert is_empty
    assert data == ['XRPUSDT', '0.75', 'Long']


@pytest.mark.asyncio
async def test_trigger(caplog):
    caplog.set_level(logging.INFO)

    client_mock = MagicMock()
    symbol = 'XRPUSDT'
    signal = 'Long'
    close_price = 0.75

    await trigger(client_mock, symbol, signal, close_price)
    assert f'{symbol} {close_price} {signal}' in caplog.text


@pytest.mark.asyncio
async def test_monitor_symbol():
    client_mock = MagicMock()
    symbol = 'XRPUSDT'
    interval = '3m'
    length = 20
    num_std_dev = 2

    await monitor_symbol(client_mock, symbol, interval, length, num_std_dev)

    # Add your assertions here


@pytest.mark.asyncio
async def test_monitor_symbols():
    client_mock = MagicMock()
    symbols = ['XRPUSDT', 'ATOMUSDT']
    interval = '3m'
    length = 20
    num_std_dev = 2

    await monitor_symbols(client_mock, symbols, interval, length, num_std_dev)

    # Add your assertions here
