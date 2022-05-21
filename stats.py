#!/usr/bin/python3

import datetime
import time
from erdpy.accounts import Account
from erdpy.transactions import BunchOfTransactions, Transaction #, TransactionWatcher
from erdpy.proxy import ElrondProxy
from operator import itemgetter

def current_milli_time():
  return round(time.time() * 1000)
  
def milli_to_time(milliseconds):
  date = datetime.datetime.fromtimestamp(milliseconds/1000.0)
  date = date.strftime('%Y-%m-%d %H:%M:%S')
  return date

def milli_to_sec(milliseconds):
  return milliseconds/1000

class TransData():
    def __init__(self, hash: str, start: int):
        self.hash = hash
        self.start = start
    def set_data(self, data: dict):
      self.data = data

def milli_elrond_to_time(milliseconds):
  date = datetime.datetime.fromtimestamp(milliseconds)
  date = date.strftime('%Y-%m-%d %H:%M:%S')
  return date

def create_transaction(nonce, amount, sender, receiver, gas_price, gas_limit, data, chain_id_version):
  return "hola"

NUM_TRANS = 10
# SEC_WAIT = 40
TIMEOUT = 1

address = "erd1wumnmqkg0xx48xeyqh4hkm29vldtgdk047cum2vz0vqyx3mmmq2qeh6e2h";
contractAddress = "erd1qqqqqqqqqqqqqpgqmd2plp8mf07qrfguhsqh2y08fvhn3ky9mq2qteqxk0";
token = f"554f432d643133396262" # UOC-d139bb
proxy = ElrondProxy("https://devnet-gateway.elrond.com")
# network settings
network_config = proxy.get_network_config()
# account = Account(pem_file="~/wallet/wallet1.pem")
# account = Account(key_file="myWallet.json", pass_file="myPass.txt")
sender = Account(pem_file="~/wallet/wallet2.pem")
sender.sync_nonce(proxy)
# gas_price = proxy.estimate_gas_price()
gas_price = network_config.min_gas_price 
gas_limit = 5000000

start_time = current_milli_time()


# print('Sequential')
# # sending transactions sequentially (send_wait_result methods)
# # parallel execution is not used
# for i in range(NUM_TRANS):
#   tx = Transaction()
#   tx.nonce = sender.nonce + i
#   tx.value = "10" 
#   tx.sender = sender.address.bech32()
#   tx.receiver = contractAddress
#   tx.gasPrice = gas_price
#   tx.gasLimit = gas_limit
#   tx.data = f"addLiquidityEgld@" + token;
#   tx.chainID = "D"
#   tx.version = 1
#   tx.sign(sender)
#   start_time = current_milli_time()
#   result = tx.send_wait_result(proxy, TIMEOUT)
#   print(f"Sending {NUM_TRANS} transactions sequentially...")
#   end_time = current_milli_time()
#   print(f"Start time: {milli_to_time(start_time)} - End time: {milli_to_time(end_time)}- is_done: {result.is_done()} - get_hash: {result.get_hash()} ")
#   print(result.is_done())
#   print(result.get_hash())
#   # item = TransData(result, current_milli_time())
#   sender.nonce += 1
  

print(f"Starting parallel {milli_to_time(current_milli_time())}")
# sending a bunch of transactions together
transactions: BunchOfTransactions = BunchOfTransactions()
for i in range(NUM_TRANS):
  tx = Transaction()
  tx.nonce = sender.nonce + i
  tx.value = "10" 
  tx.sender = sender.address.bech32()
  tx.receiver = contractAddress
  tx.gasPrice = gas_price
  tx.gasLimit = gas_limit
  tx.data = f"addLiquidityEgld@" + token;
  tx.chainID = "D"
  tx.version = 1
  tx.sign(sender)
  # result = tx.send_wait_result(proxy, 6)
  start_time = current_milli_time()
  transactions.add_prepared(tx)
send_time = current_milli_time()
num, hashes = transactions.send(proxy)

i = 0
wait = True
found = []
found_data = []
while len(found) < NUM_TRANS:
  try:
    data = proxy.get_transaction(hashes[str(i)], with_results=True)
    dictio = data.to_dictionary()
    # scResults = dictio['smartContractResults']
    # dictioSC = scResults[0].to_dictionary()
    # print(dictioSC)
    print(i)
    if dictio['status'] == 'success' and not found.__contains__(hashes[str(i)]):
      ti, st, ep, ro, so, de = itemgetter('timestamp', 'status', 'epoch', 'round', 'sourceShard', 'destinationShard')(dictio)
      obj = {
        'hash': hashes[str(i)],
        'send_time': send_time,
        'end_time': current_milli_time(),
        'timestamp': ti,
        'status': st,
        'epoch': ep,
        'round': ro,
        'sourceShard': so,
        'destinationShard': de
      }
      found_data.append(obj)
      found.append(hashes[str(i)]) 
  except:
    pass
  finally:
    i = (i+1)%NUM_TRANS

for item in found_data:
    print(f"----------------------------------------")
    print(f"Hash: {item['hash']} - Status: {item['status']}")
    print(f"Elrond age: {milli_elrond_to_time(item['timestamp'])} - Send time: {milli_to_time(item['send_time'])} - End time: {milli_to_time(item['end_time'])} Diff (end t. - send t.): {item['end_time']-item['send_time']}")
    print(f"Epoch: {item['epoch']} - Round: {item['round']} - Source shard: {item['sourceShard']} - Destination shard: {item['destinationShard']}")

# transactionsData = []
# for i in range(len(hashes)):
#   print(hashes[str(i)])
#   data = proxy.get_transaction(hashes[str(i)], with_results=True)
#   dictio = data.to_dictionary()
#   transactionsData.append(dictio)
#   print(transactions[i].hash, milli_to_time(start_time), milli_to_time(end_time), milli_to_time(transactions[i].start),  milli_elrond_to_time(transactions[i].data['timestamp']))
#   print(f"----------------------------------------")
#   print(f"Nonce: {transactions[i].data['nonce']} Hash: {transactions[i].hash}")
#   print(f"Epoch: {transactions[i].data['epoch']} - Round: {transactions[i].data['round']} - Source shard: {transactions[i].data['sourceShard']} - Destination shard: {transactions[i].data['destinationShard']}")
#   print(f"Start time: {milli_to_time(start_time)} - Timestamp: {milli_elrond_to_time(transactions[i].data['timestamp'])} ")
#   print(f"Status: {transactions[i].data['status']} ")

# for item in transactionsData:
#   print(item['status'])
# print(num, hashes)
# for i in range(NUM_TRANS):
#   data = proxy.get_transaction(transactions[i].hash, with_results=True)
#   dictio = data.to_dictionary()
#   transactions[i].set_data(dictio)
#   # print(transactions[i].hash, milli_to_time(start_time), milli_to_time(end_time), milli_to_time(transactions[i].start),  milli_elrond_to_time(transactions[i].data['timestamp']))
#   print(f"----------------------------------------")
#   print(f"Nonce: {transactions[i].data['nonce']} Hash: {transactions[i].hash}")
#   print(f"Epoch: {transactions[i].data['epoch']} - Round: {transactions[i].data['round']} - Source shard: {transactions[i].data['sourceShard']} - Destination shard: {transactions[i].data['destinationShard']}")
#   print(f"Start time: {milli_to_time(start_time)} - Timestamp: {milli_elrond_to_time(transactions[i].data['timestamp'])} ")
#   print(f"Status: {transactions[i].data['status']} ")
# watcher = TransactionWatcher(proxy)


# print(f"Sent {num} transactions:")
# print(hashes)
