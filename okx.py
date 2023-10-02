import asyncio
import ccxt.async_support as ccxt
import random

#----main-options----#
switch_cex = "okx"       # binance, mexc, kucoin, gate, okx, huobi, bybit
symbolWithdraw = "ETH"      # символ токена
network = "Arbitrum One"     # ID сети
proxy_server = ""

#----second-options----#
amount = [0.001, 0.001]          # минимальная и максимальная сумма
decimal_places = 5           # количество знаков, после запятой для генерации случайных чисел
delay = [1, 5]             # минимальная и максимальная задержка
shuffle_wallets = "no"       # нужно ли мешать кошельки yes/no
#----end-all-options----#

class API:
    # binance API
    binance_apikey = "your_api"
    binance_apisecret = "your_api_secret"
    # okx API
    okx_apikey = ""
    okx_apisecret = ""
    okx_passphrase = ""
    # bybit API
    bybit_apikey = "your_api"
    bybit_apisecret = "your_api_secret"
    # gate API
    gate_apikey = "your_api"
    gate_apisecret = "your_api_secret"
    # kucoin API
    kucoin_apikey = "your_api"
    kucoin_apisecret = "your_api_secret"
    kucoin_passphrase = "your_api_password"
    # mexc API
    mexc_apikey = "your_api"
    mexc_apisecret = "your_api_secret"
    # huobi API
    huobi_apikey = "your_api"
    huobi_apisecret = "your_api_secret"

proxies = {
  "http": proxy_server,
  "https": proxy_server,
}

async def okx_withdraw(address, amount_to_withdrawal, wallet_number):
    exchange = ccxt.okx({
        'apiKey': API.okx_apikey,
        'secret': API.okx_apisecret,
        'password': API.okx_passphrase,
        'enableRateLimit': True,
        'proxies': proxies,
    })

    try:
        chainName = symbolWithdraw + "-" + network
        fee = await get_withdrawal_fee(symbolWithdraw, chainName, exchange)
        await exchange.withdraw(symbolWithdraw, amount_to_withdrawal, address,
            params={
                "toAddress": address,
                "chainName": chainName,
                "dest": 4,
                "fee": fee,
                "pwd": '-',
                "amt": amount_to_withdrawal,
                "network": network
            }
        )

        print(f'\n>>>[OKx] Вывел {amount_to_withdrawal} {symbolWithdraw} ', flush=True)
        print(f'    [{wallet_number}]{address}', flush=True)
    except Exception as error:
        print(f'\n>>>[OKx] Не удалось вывести {amount_to_withdrawal} {symbolWithdraw}: {error} ', flush=True)
        print(f'    [{wallet_number}]{address}', flush=True)

async def choose_cex(address, amount_to_withdrawal, wallet_number):
    if switch_cex == "okx":
        await okx_withdraw(address, amount_to_withdrawal, wallet_number)
    else:
        raise ValueError("Неверное значение CEX. Поддерживаемые значения: binance, okx, bybit, gate, huobi, kucoin, mexc.")

async def get_withdrawal_fee(symbolWithdraw, chainName, exchange):
    currencies = await exchange.fetch_currencies()
    for currency in currencies:
        if currency == symbolWithdraw:
            currency_info = currencies[currency]
            network_info = currency_info.get('networks', None)
            if network_info:
                for network in network_info:
                    network_data = network_info[network]
                    network_id = network_data['id']
                    if network_id == chainName:
                        withdrawal_fee = currency_info['networks'][network]['fee']
                        if withdrawal_fee == 0:
                            return 0
                        else:
                            return withdrawal_fee
    raise ValueError(f"     не могу получить сумму комиссии, проверьте значения symbolWithdraw и network")

async def shuffle(wallets_list, shuffle_wallets):
    numbered_wallets = list(enumerate(wallets_list, start=1))
    if shuffle_wallets.lower() == "yes":
        random.shuffle(numbered_wallets)
    elif shuffle_wallets.lower() == "no":
        pass
    else:
        raise ValueError("\n>>> Неверное значение переменной 'shuffle_wallets'. Ожидается 'yes' или 'no'.")
    return numbered_wallets

async def main_withdraw():
    try:
        with open("wallets.txt", "r") as f:
            wallets_list = [row.strip() for row in f if row.strip()]
            numbered_wallets = await shuffle(wallets_list, shuffle_wallets)
            print(f'Количество кошельков: {len(wallets_list)}')
            print(f"CEX: {switch_cex}")
            print(f"Сумма: {amount[0]} - {amount[1]} {symbolWithdraw}")
            print(f"Сеть: {network}")
            await asyncio.sleep(random.randint(2, 4))

            tasks = []
            for wallet_number, address in numbered_wallets:
                amount_to_withdrawal = round(random.uniform(amount[0], amount[1]), decimal_places)
                tasks.append(choose_cex(address, amount_to_withdrawal, wallet_number))
                await asyncio.sleep(random.randint(delay[0], delay[1]))

            await asyncio.gather(*tasks)

        return True  # Возвращаем True в случае успешного выполнения
    except Exception as e:
        print(f'Произошла ошибка: {e}')
        return False  # Возвращаем False в случае ошибки
