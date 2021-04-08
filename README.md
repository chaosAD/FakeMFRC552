## Installing fake MRFC522 library

To install this library, issue:
```bash
pip install https://github.com/chaosAD/FakeMfrc522/archive/refs/heads/master.zip
```

## Purpose

The purpose of this fake library is to allow rapid development of Mifare RFID software development and also testing. The benefits of this library are: 

1. Do not need to have the actual card reader/writer
2. Do not need RFID cards
3. Can create as many virtual cards as desired
4. Can be used for rapid testing of software
5. Will not suffer card lock or lost keys

## Future Development

Current, this version only supports basic reading and writing without the implementation of the security features. This will be added in the future.