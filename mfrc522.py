import json, os, re, threading, time
from collections import OrderedDict

class SimpleMFRC522:
    __data = None
    __writer = None
    __access_delay = 0.12               # 120ms

    @staticmethod
    def load_data(data):
        with threading.Lock():
            SimpleMFRC522.__data = data

    @staticmethod
    def set_writer(rfid_writer):
        with threading.Lock():
            SimpleMFRC522.__writer = rfid_writer

    @staticmethod
    def set_access_delay(delay):
        with threading.Lock():
            SimpleMFRC522.__access_delay = delay

    def read(self):
        return self.read_sector(2)

    def read_sector(self, sector):
        id, text = self.read_sector_no_block(sector)
        while not id:
            id, text = self.read_sector_no_block(sector)
        return id, text

    def write_id(self, new_id):
        data = new_id[:4] + self.__get_block(0)[4:16]
        self.__write_block(0, data)
        if SimpleMFRC522.__writer:
            SimpleMFRC522.__writer.update()

    def read_id(self):
        id = self.read_id_no_block()
        while not id:
            id = self.read_id_no_block()
        return id

    def read_id_no_block(self):
        self.__get_data_snapshot()
        if self.data_ is None:
            return None
        return self.uid_to_num(self.__get_block(0))

    def read_no_block(self):
        return self.read_sector_no_block(self, 2)

    def write(self, text):
        return self.write_sector(text, 2)

    def write_sector(self, text, sector):
        id, text_in = self.write_sector_no_block(text, sector)
        while not id:
            id, text_in = self.write_sector_no_block(text, sector)
        return id, text_in

    def write_no_block(self, text):
        return self.write_sector_no_block(text, 2)

    def read_sector_no_block(self, sector):
        self.__get_data_snapshot()
        if self.data_ is None:
            return None, None
        block = sector * 4
        if block+2 >= 16:
            raise IndexError('Sector out of range. Please use 0 <= sector < 4.')
        blocks = [block, block+1, block +2]
        data = []
        for block_num in blocks:
            block = self.__get_block(block_num)
            if block:
                data += block
        text_read = ''
        if data:
            text_read = ''.join(chr(i) for i in data)
        id = self.uid_to_num(self.__get_block(0))
        return id, text_read

    def write_sector_no_block(self, text, sector):
        self.__get_data_snapshot()
        if self.data_ is None:
            return None, None
        block = sector * 4
        if block+2 >= 16:
            raise IndexError('Sector out of range. Please use 0 <= sector < 4.')
        if block == 0:
            blocks = [block+1, block +2]
        else:
            blocks = [block, block+1, block +2]
        data = []
        data.extend(bytearray(text.ljust(len(blocks) * 16).encode('ascii')))
        i = 0
        for block_num in blocks:
            self.__write_block(block_num, data[(i*16):(i+1)*16])
            i += 1
        if SimpleMFRC522.__writer:
            SimpleMFRC522.__writer.update()
        id = self.uid_to_num(self.__get_block(0))
        return id, text[0:(len(blocks) * 16)]

    def uid_to_num(self, uid):
        n = 0
        for i in range(4):
            n = (n << 8) + uid[i]
        return n

    def __get_data_snapshot(self):
        with threading.Lock():
            self.data_ = SimpleMFRC522.__data

    def __get_block(self, block_num):
        if self.data_ is None:
            raise SystemError('RFID block is missing')
        block_name = f'block_{block_num:02d}'
        if block_name in self.data_:
            time.sleep(SimpleMFRC522.__access_delay)
            return self.data_[block_name]
        raise SystemError('RFID block is missing')

    def __normalize_block(self, block):
        num = len(block)
        if num < 16:
            block += [0] * (16 - num)
            return block
        return block[:16]

    def __write_block(self, block_num, new_data):
        if self.data_ is None:
            raise SystemError('RFID block is missing')
        block_name = f'block_{block_num:02d}'
        if block_name in self.data_:
            time.sleep(SimpleMFRC522.__access_delay)
            self.data_[block_name] = self.__normalize_block(new_data)
            return
        raise SystemError(f"RFID '{block_name}' is missing")

class CardStorage():
    __n_digits = 2

    def __init__(self, filename, num_digits_of_card=None):
        with threading.Lock():
            self.filename = filename
            self.cards = None
            if num_digits_of_card is not None:
                CardStorage.__n_digits = num_digits_of_card

    @staticmethod
    def prettify_cards_info(cards, indent=2):
        with threading.Lock():
            cards = OrderedDict(sorted(cards.items()))
            for c in cards:
                cards[c] = OrderedDict(sorted(cards[c].items()))
        keys = cards.keys()
        spaces = ' ' * indent
        txt = '{\n'
        for k in keys:
            txt += spaces + f'"{k}": ' + '{\n'
            _2_spaces = spaces * 2
            for b in cards[k]:
                txt += _2_spaces + f'"{b}": {cards[k][b]},' + '\n'
            txt = txt[:-2] + '\n' + spaces + '},\n'
        return txt[:-2] + '\n' + '}'

    @staticmethod
    def assert_valid_card_name(card_name, max_num):
        c = card_name.strip().split('_')
        if len(c) != 2 or c[0].lower() != 'card' or not c[1].isnumeric() or  \
            int(c[1]) < 0 or int(c[1]) > max_num:
            raise AssertionError(f"Illegal card name: '{card_name}'")

    @staticmethod
    def normalize_block(block):
        num = len(block)
        if num < 16:
            block += [0] * (16 - num)
            return block, True
        if num == 16:
            return block, False
        return block[:16], True

    @staticmethod
    def __normalize_name(name, constant, num_of_digits):
        actual_len = len(name)
        new_name = name.strip()
        modified = True if len(new_name) != actual_len else False
        c = new_name.split('_')
        if len(c) != 2:
            raise ValueError(f"'{new_name}' is an invalid name")
        if not c[1].isnumeric():
            raise TypeError(f"The '{c[1]}' is not a number in the '{name}'")
        num = str(int(c[1])).zfill(num_of_digits)
        txt = c[0]
        if txt.lower() != txt:
            txt = txt.lower()
            modified = True
        constant = constant.lower()
        if txt != constant:
            raise ValueError(f"Expecting '{constant}' in the '{name}', but got '{c[0]}'")
        if num != c[1]:
            modified = True
        return txt + '_' + num, modified

    @staticmethod
    def normalize_block_name(block_name, num_of_digits):
        return CardStorage.__normalize_name(block_name, 'block', num_of_digits)

    @staticmethod
    def normalize_card_name(card_name, num_of_digits):
        return CardStorage.__normalize_name(card_name, 'card', num_of_digits)

    @staticmethod
    def get_card_name(card_num):
        return 'card_' + str(card_num).zfill(CardStorage.__n_digits)

    @staticmethod
    def normalize_cards(cards):
        changed = False
        for card in cards:
            CardStorage.assert_valid_card_name(card, 99)
            card_name, rectified = CardStorage.normalize_card_name(card, CardStorage.__n_digits)
            if rectified:
                cards[card_name] = cards.pop(card)
                changed = True
            card_ = cards[card]
            for block_name in card_:
                new_name, rectified = CardStorage.normalize_block_name(block_name, 2)
                if rectified:
                    card_[new_name] = card_.pop(block_name)
                    changed = True
            for i in range(16):
                block_name = f'block_{i:02d}'
                if block_name not in cards[card_name]:
                    cards[card_name][block_name] = [
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
                    ]
                    changed |= True
                else:
                    card_ = cards[card_name]
                    card_[block_name], rectified = CardStorage.normalize_block(card_[block_name])
                    changed |= rectified
        return changed

    def read(self):
        with threading.Lock():
            with open(self.filename, "r") as f:
                self.cards = json.load(f)
                if not self.cards:
                    raise Exception(f"There is no card information in '{self.filename}'")
                if self.normalize_cards(self.cards):
                    self.update()
                return self.cards

    def update(self):
        with threading.Lock():
            with open(self.filename, "w") as f:
                f.write(CardStorage.prettify_cards_info(self.cards))
