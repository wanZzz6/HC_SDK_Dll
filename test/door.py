import time

from src.interface import HKDoor


def del_all_card(sdk, cards_numbers: list):
    for card in cards_numbers:
        sdk.door_del_one_card(str(card))


if __name__ == '__main__':
    # tool = HKDoor('10.86.77.119', 'admin', 'admin777')  # 门禁
    tool = HKDoor('10.10.111.170', 'admin', '2020')  # 门禁2
    tool.sys_login()

    ##############################
    # tool.setup_alarm_chan()
    # tool.door_open(1)
    # time.sleep(2)
    ###############################
    all_cards = tool.door_get_all_card()
    print(all_cards)
    ###############################
    # tool.door_get_one_card('9527')
    ###############################
    # tool.door_set_one_card('1203', byDoorRight='1')
    ###############################
    # tool.door_del_one_card('921005')
    tool.sys_clean_up()
