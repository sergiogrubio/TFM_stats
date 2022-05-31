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

def milli_to_sec_round(milliseconds):
  return int((milliseconds/1000))%60

def milli_to_min_round(milliseconds):
  return int((milliseconds/(1000*60)))%60

def milli_to_sec(milliseconds):
  return (milliseconds/1000)%60

def milli_to_min(milliseconds):
  return (milliseconds/(1000*60))%60

def milli_elrond_to_time(milliseconds):
  date = datetime.datetime.fromtimestamp(milliseconds)
  date = date.strftime('%Y-%m-%d %H:%M:%S')
  return date

def send_transactions(proxy, num_trans, value, contract_address, gas_price, gas_limit, data , chain_id, version):
  transactions: BunchOfTransactions = BunchOfTransactions()
  for i in range(num_trans):
    tx = Transaction()
    tx.nonce = sender.nonce + i
    tx.value = str(value)
    tx.sender = sender.address.bech32()
    tx.receiver = contract_address
    tx.gasPrice = gas_price
    tx.gasLimit = gas_limit
    tx.data = data
    tx.chainID = chain_id
    tx.version = version
    tx.sign(sender)
    transactions.add_prepared(tx)
  start_time = current_milli_time()
  num, hashes = transactions.send(proxy)
  return start_time, num, hashes

def process_found_data(found_data):
  start_time = 9999999999999
  end_time = 0
  for item in found_data:
    # start time is always the same with this implementation (BunchOfTransactions)
    # I used it before sending transactions one by one
    if start_time > int(item['start_time']):
      start_time = int(item['start_time'])
    if end_time < int(item['end_time']):
      end_time = int(item['end_time'])
    print(f"----------------------------------------")
    print(f"Hash: {item['hash']} - Status: {item['status']}")
    spent_time = item['end_time']-item['start_time']
    print(f"Elrond age: {milli_to_time(item['start_time'])} {milli_elrond_to_time(item['timestamp'])} - Start time: {milli_to_time(item['start_time'])} - End time: {milli_to_time(item['end_time'])} - Diff (end t. - start t.): {spent_time}")
    print(f"Epoch: {item['epoch']} - Round: {item['round']} - Source shard: {item['sourceShard']} - Destination shard: {item['destinationShard']}")
  result = end_time - start_time
  print(f"{len(found_data)} transactions executed successfully in {milli_to_min_round(result)} minutes {milli_to_sec_round(result)} seconds ({result} ms).")   
  print(f"They were sent from this computer at {milli_to_time(start_time)}.") 
  print(f"They arrived to an Elrond devnet node at {milli_to_time(start_time)}.") 
  print(f"This computer detected querying the Elrond API that they ended at {milli_to_time(end_time)}.")

def waiting_for_results(proxy, start_time, hashes):
  i = 0
  found = []
  found_data = []
  while len(found) < NUM_TRANS:
    try:
      data = proxy.get_transaction(hashes[str(i)], with_results=True)
      dictio = data.to_dictionary()
      print(i, end = "\r")
      if dictio['status'] == 'success' and not found.__contains__(hashes[str(i)]):
        ti, st, ep, ro, so, de = itemgetter('timestamp', 'status', 'epoch', 'round', 'sourceShard', 'destinationShard')(dictio)
        obj = {
          'hash': hashes[str(i)],
          'start_time': start_time,
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
  return found_data

NUM_TRANS = 5
# SEC_WAIT = 40
TIMEOUT = 1
TOKEN = f"4142432d313039373339" # ABC-109739
FUNCTION = "addLiquidityEgld"
AMOUNT_EGLD = 10000000000000000 # 0.01
ONE_EGLD = 1000000000000000000
CONTRACT_ADDRESS = "erd1qqqqqqqqqqqqqpgq578zh88hskf9efwzyhkf64el7d6ve3lrsn2qwkvmt2";

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

print(f"Starting parallel {milli_to_time(current_milli_time())}")
print(f"Funding ABC-xEGLD liquidity pool with {AMOUNT_EGLD*NUM_TRANS/ONE_EGLD} xEGLD among {NUM_TRANS} transactions")
print(f"Please wait a few seconds")
# sending a bunch of transactions together
start_time, num, hashes = send_transactions(proxy, NUM_TRANS, AMOUNT_EGLD, CONTRACT_ADDRESS, gas_price , gas_limit, FUNCTION + "@" + TOKEN, "D", 1)
print(f"{num} transactions were sent")

# waiting for the transaction to end, only with success status
found_data = waiting_for_results(proxy, start_time, hashes)

# process results
process_found_data(found_data)  

