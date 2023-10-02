import asyncio
import random
from dmail_new.dmail import dmail
from my_swap_new.swaper import eth_to_stable, stable_to_eth
from my_swap_new.token_config import TOKEN_CONFIG, STABLECOINS
from zk_lend_new.lending import deposite, withdraw
from loguru import logger
from sent_eth.sent import send_eth
from withdraw.sub_accs import withdraw_all_funds_to_main_account


# Функция для выполнения операций для одного кошелька
async def perform_operations_for_wallet(address, private_key, to_addresses):
    # Случайное количество итераций для выполнения операций
    num_iterations = random.randint(3, 4)
    logger.info(f"Number of iterations for account {address}: {num_iterations}")

    for _ in range(num_iterations):
        # Случайный выбор стейблкоина для свапа
        stablecoin = random.choice(STABLECOINS)
        stablecoin_config = TOKEN_CONFIG[stablecoin]

        # Случайное количество эфиров для свапа
        amount_to_swap = random.uniform(0.0005, 0.0008)

        # Определение операций
        operations = ['dmail', 'eth_to_stable', 'stable_to_eth', 'deposite', 'withdraw']
        random.shuffle(operations)
        # Если 'withdraw' перед 'deposit', меняем их местами
        if operations.index('withdraw') < operations.index('deposite'):
            operations.remove('withdraw')
            operations.append('withdraw')

        # Если 'stable_to_eth_swap' перед 'eth_to_stable_swap', меняем их местами
        if operations.index('stable_to_eth') < operations.index('eth_to_stable'):
            operations.remove('stable_to_eth')
            operations.append('stable_to_eth')
        # Выполнение операций
        for operation in operations:
            if operation == 'dmail':
                await dmail(private_key, address)
            elif operation == 'eth_to_stable':
                await eth_to_stable(private_key, stablecoin_config, stablecoin, amount_to_swap, address)
            elif operation == 'stable_to_eth':
                await stable_to_eth(private_key, stablecoin_config, stablecoin, amount_to_swap, address)
            elif operation == 'deposite':
                await deposite(private_key, address)
            elif operation == 'withdraw':
                await withdraw(private_key, address)

            # Генерируем случайное время задержки между 10 и 15 секундами
            delay = random.uniform(5, 10)

            # Добавляем задержку
            await asyncio.sleep(delay)
            logger.info(f"Подождал {delay} сек.")

    # После завершения всех операций, отправляем эфиры
    await send_eth(private_key, address, to_addresses)


async def main():
    # Выполните функцию `withdraw_all_funds_to_main_account` сразу в начале
    success = await withdraw_all_funds_to_main_account()

    if success:
        logger.success("Все средства были успешно переведены на основной счет. Продолжаем выполнение скрипта.")
    else:
        logger.error("Произошла ошибка при переводе средств. Скрипт завершается.")

    # Считываем приватные ключи из файла 'private_keys.txt'
    with open('private_keys.txt', 'r') as f:
        private_keys = f.read().strip().split('\n')

    # Считываем адреса из файла 'addresses.txt'
    with open('addresses.txt', 'r') as f:
        addresses = f.read().strip().split('\n')

    # Считываем адреса для отправки из файла 'to.txt'
    with open('to.txt', 'r') as to_file:
        to_addresses = to_file.read().strip().split('\n')

    # Проверяем, что количество приватных ключей и адресов совпадает
    if len(private_keys) != len(addresses):
        print("Количество приватных ключей и адресов должно совпадать.")
        return

    # Проверяем, что количество адресов для отправки соответствует количеству кошельков
    if len(to_addresses) != len(addresses):
        print("Количество адресов для отправки должно совпадать с количеством кошельков.")
        return

    # Определите количество кошельков, которые должны выполняться одновременно
    num_simultaneous_wallets = 5  # Вы можете настроить это число

    # Создайте задачи для одновременного выполнения
    tasks = []
    for i, address in enumerate(addresses):
        # Создаем копию функции perform_operations_for_wallet с уникальными параметрами
        task = perform_operations_for_wallet(address, private_keys[i], to_addresses[i])
        tasks.append(task)

        # Если достигнуто нужное количество задач, ждем их завершения, а затем запускаем новую группу
        if len(tasks) == num_simultaneous_wallets:
            await asyncio.gather(*tasks)
            tasks = []

    # Запускаем оставшиеся задачи
    if tasks:
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())