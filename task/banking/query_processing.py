from bank_service import *
import sys

"""Обработка приходящих запросов пользователя"""


def process_queries():
    bank = Bank()  # создаем экземпляр класса Bank
    while True:
        bank.options()
        option = int(input())  # выводим список доступных опций

        if option == 1:
            bank.create_account()  # создаем аккаунт

        elif option == 2:
            print("")
            print("Enter your card number:")
            user_card_number = input()
            print("Enter your PIN:")
            pin = input()
            succeed = bank.log_in(user_card_number, pin)  # пытаемся залогиниться по карте или пин-коду
            if succeed:
                print("")
                print("You have successfully logged in!")  # если успешно, сообщаем об этом
                while True:
                    bank.actions_after_log_in()  # печатаем возможные дальнейшие действия
                    action = int(input())
                    if action == 1:
                        print("")
                        bank.get_balance(user_card_number)  # запрашиваем баланс
                    elif action == 2:
                        print("Enter income:")
                        income = int(input())
                        bank.add_income(user_card_number, income)  # пополняем баланс карты
                    elif action == 3:
                        print("Transfer")  # пытаемся осуществить перевод
                        print("Enter card number:")
                        transfer_card = input()
                        if transfer_card == user_card_number:  # на один и тот же счет переводить нельзя
                            print("You can't transfer money to the same account!")
                            continue
                        if bank.luhn_algorithm(transfer_card[:15]) != transfer_card[
                            15]:  # номер карты должен удовлетворять алгоритму Луна
                            print("Probably you made a mistake in the card number. Please try again!")
                            continue
                        bank.cur.execute(f"SELECT number FROM card WHERE number = {transfer_card}")
                        if bank.cur.fetchone() is None:  # карты, на которую мы хотим перевести, нет в базе
                            print("Such a card does not exist.")
                            continue
                        print("Enter how much money you want to transfer:")
                        money = int(input())  # вводим сумму перевода
                        bank.cur.execute(f"SELECT balance FROM card WHERE number = {user_card_number}")
                        user_balance = bank.cur.fetchone()[0]
                        if user_balance < money:  # недостаточно денег для перевода
                            print("Not enough money!")
                            continue
                        bank.do_transfer(user_card_number, user_balance, transfer_card, money)  # если все ок, переводим
                    elif action == 4:
                        bank.delete_account(user_card_number)  # удаляем аккаунт по просьбе пользователя
                        break
                    elif action == 5:
                        print("")
                        print("You have successfully logged out!")  # разлогинились
                        break
                    elif action == 0:
                        sys.exit(0)  # выходим из системы

                    else:
                        print("")
                        print("Invalid action!")  # попытка недопустимой операции
            else:
                print("")
                print("Wrong card number or PIN!")  # неверный номер карты или пин-код, не залогинились

        elif option == 0:
            print("")
            print("Bye!")  # прощаемся
            break

        else:
            print("")
            print("Invalid option!")


if __name__ == '__main__':
    process_queries()
