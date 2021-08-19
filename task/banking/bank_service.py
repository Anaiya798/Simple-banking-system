import secrets
import sqlite3

"""Класс для хранения данных и обработки запросов к банку"""


class Bank:
    IIN = "400000"  # банковский ИИН, первые 5 цифр любой карты

    """Создаем экземпляр класса и базу данных, где будут храниться
    все карты, выпущенные банком, пин-коды к ним и положенные на них денежные средства"""

    def __init__(self):
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)")
        self.conn.commit()

    """Перечень доступных опций при входе пользователя в систему"""

    @staticmethod
    def options():
        print("")
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")

    """С помощью генератора случайных чисел модуля secrets (более надежного,
    чем random) получаем 9 цифр карты пользователя, следующих за ИИН"""

    def generate_can(self):
        can = None
        result = " "
        while (result is not None) or (can is None):
            can = str(secrets.randbelow(1000000000))
            self.cur.execute(f"SELECT number FROM card WHERE number = {can}")
            result = self.cur.fetchone()
            if len(can) < 9:
                can = "0" * (9 - len(can)) + can
        return can

    """Генерируем четырехзначный пин-код"""

    @staticmethod
    def generate_pin():
        pin = str(secrets.randbelow(10000))
        if len(pin) < 4:
            pin = "0" * (4 - len(pin)) + pin
        return pin

    """С помощью алгоритма Луна (https://calculatorium.ru/it/luhn-algorithm)
    получаем последнюю цифру карты пользователя"""

    @staticmethod
    def luhn_algorithm(sequence):
        sum_digits = 0
        for i in range(1, 16):
            digit = int(sequence[i - 1])
            if i % 2:
                digit *= 2
            if digit > 9:
                digit -= 9
            sum_digits += digit
        return str((10 - sum_digits % 10) % 10)

    """После того как номер и пин-код были полностью сгенерированы, 
    карту необходимо добавить в базу"""

    def insert_card_into_db(self, account_id, card_number, pin):
        self.cur.execute(f"INSERT INTO card (id, number, pin) VALUES ({int(account_id)}, {card_number}, {pin})")
        self.conn.commit()

    """Создаем аккаунт пользователя, выдавая ему 
    персональный номер карты и пин-код"""

    def create_account(self):
        account_id = self.generate_can()
        checksum = self.luhn_algorithm(self.IIN + account_id)
        card_number = self.IIN + account_id + checksum
        pin = self.generate_pin()
        self.insert_card_into_db(account_id, card_number, pin)
        print("")
        print("Your card has been created")
        print(f"Your card number: \n{card_number}")
        print(f"Your card PIN: \n{pin}")

    """Попытка пользователя залогиниться по номеру карты и пин-коду.
    Проверяем, есть ли такие в базе"""

    def log_in(self, card_number, pin):
        self.cur.execute(f"SELECT pin FROM card WHERE number = {card_number}")
        affected_row = self.cur.fetchone()
        if (affected_row is not None) and (affected_row[0] == pin):
            return True
        else:
            return False

    """Список опций для залогинившихся пользователей"""

    @staticmethod
    def actions_after_log_in():
        print("")
        print("1. Balance")
        print("2. Add income")
        print("3. Do transfer")
        print("4. Close account")
        print("5. Log out")
        print("0. Exit")

    """Вывод баланса карты"""

    def get_balance(self, card_number):
        self.cur.execute(f"SELECT balance FROM card WHERE number = {card_number}")
        print("Balance:", self.cur.fetchone()[0])

    """Добавление денежных средств на карту"""

    def add_income(self, card_number, income):
        self.cur.execute(f"SELECT balance FROM card WHERE number = {card_number}")
        user_balance = self.cur.fetchone()[0]
        self.cur.execute(f"UPDATE card SET balance = {user_balance + income} WHERE number == {card_number}")
        self.conn.commit()
        print("Income was added!")

    """Перевод денежных средств между картами"""

    def do_transfer(self, user_card_number, user_balance, transfer_card, money):
        self.cur.execute(
            f"UPDATE card SET balance = {user_balance - money} WHERE number == {user_card_number}")
        self.conn.commit()
        self.cur.execute(f"SELECT balance FROM card WHERE number = {transfer_card}")
        transfer_receiver_balance = self.cur.fetchone()[0]
        self.cur.execute(
            f"UPDATE card SET balance = {transfer_receiver_balance + money} WHERE number == {transfer_card}")
        self.conn.commit()
        print("Transfer done!")

    """Удаление аккаунта пользователем и удаление сведений об
    аккаунте из базы данных"""

    def delete_account(self, card_number):
        self.cur.execute(f"DELETE FROM card WHERE number = {card_number}")
        self.conn.commit()
        print("The account has been closed!")
