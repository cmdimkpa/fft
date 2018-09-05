import datetime,cPickle,os

global account_object_store,Dir,cache

Dir = os.getcwd()
if "\\" in Dir:
    # Windows
    cache = Dir+'\\account_object_store'
else:
    # UNIX-like
    cache = Dir+'/account_object_store'

def persist_account_store(current_state):
    global account_object_store
    account_object_store = current_state
    p = open(cache,"wb+")
    p.write(cPickle.dumps(current_state))
    p.close()

def read_account_store():
    p = open(cache,'rb+')
    account_object_store = cPickle.loads(p.read())
    p.close()
    return account_object_store

# Invoke Account Object Store on startup

try:
    account_object_store = read_account_store()
except:
    persist_account_store([])  # initialize account store
    account_object_store = read_account_store()

def return_account_by_id(account_id):
    try:
        return [account for account in account_object_store if account.id == account_id][0]
    except:
        return "not_found"

def update_account_by_id(account_id,updated_account):
    global account_object_store
    account = return_account_by_id(account_id)
    if account != "not_found":
        # TEST:
        # are the two accounts identical?
        # is updated_account an account object?
        try:
            if account.id == updated_account.id:
                account_index = account_object_store.index(account)
                # update account object store
                account_object_store[account_index] = updated_account
                # persist to cache
                persist_account_store(account_object_store)
            else:
                pass
        except:
            pass

def is_unique_id(id):
    object = return_account_by_id(id)
    if object == "not_found":
        return True
    else:
        return False

def timestamp():
    return datetime.datetime.today()

def can_withdraw(sending_account,outgoing_amount):
    if outgoing_amount <= sending_account.balance():
        return True
    else:
        return False

def valid_amount(amount):
    try:
        float(amount)
        return True
    except:
        return False

def query_balance_range_all(min,max):
    # return all account objects with balance in a given range
    try:
        min,max = map(float([min,max]))
        min = min([min,max])
        max = max([min,max])
        return [account for account in account_object_store if account.balance() >= min and account.balance() <= max]
    except:
        return "check your arguments"

def account_statement_by_range(min,max):
    accounts = query_balance_range_all(min,max)
    if accounts not in ["check your arguments",[]]:
        report = {}
        for account in accounts:
            report[account.id] = {}
            report[account.id]["incoming"] = account.incoming
            report[account.id]["outgoing"] = account.outgoing
        return report
    else:
        return "there was no result for your query (check arguments)"

def funds_transfer_interface(sender_id,receiver_id,amount):
    sender_account = return_account_by_id(sender_id);
    receiver_account = return_account_by_id(receiver_id);
    if sender_account != "not_found" and receiver_account != "not_found":
        if can_withdraw(sender_account,amount):
            # fix transaction date
            transaction_date = timestamp()
            # credit receiver account
            receiver_account.credits.append(amount)
            # debit sender account
            sender_account.debits.append(amount)
            # update sender's log
            sender_account.outgoing["id"].append(receiver_account.id)
            sender_account.outgoing["location"].append(receiver_account.location)
            sender_account.outgoing["date"].append(transaction_date)
            sender_account.outgoing["amount"].append(amount)
            # update receiver's log
            receiver_account.incoming["id"].append(sender_account.id)
            receiver_account.incoming["location"].append(sender_account.location)
            receiver_account.incoming["date"].append(transaction_date)
            receiver_account.incoming["amount"].append(amount)
            # update sender's account
            update_account_by_id(sender_id,sender_account)
            # update receiver's account
            update_account_by_id(receiver_id,receiver_account)
            return "success: %s was transferred from: %s to: %s at: %s" % (amount,sender_id,receiver_id,transaction_date)
        else:
            return "insufficient funds, cannot transfer amount: %s" % amount
    else:
        return "one or more accounts involved in this transaction don't exist"

class Account:
    def __init__(self,account_id,location):
        self.id = account_id;
        self.location = location;
        self.credits = [];
        self.debits = [];
        self.incoming = {
            "id":[],
            "location":[],
            "date":[],
            "amount":[]
        };
        self.outgoing = {
            "id":[],
            "location":[],
            "date":[],
            "amount":[]
        };
    def balance(self):
        return sum(self.credits) - sum(self.debits)
    def send(self,receiver_id,amount):
        if valid_amount(amount):
            return funds_transfer_interface(self.id,receiver_id,amount)
        else:
            return "invalid amount selected: %s" % amount
    def self_fund(self,amount):
        if not valid_amount(amount):
            return "invalid amount selected: %s" % amount
        transaction_date = timestamp()
        self.credits.append(amount)
        self.incoming["id"].append(self.id)
        self.incoming["location"].append(self.location)
        self.incoming["date"].append(transaction_date)
        self.incoming["amount"].append(amount)
        # update this account in store
        update_account_by_id(self.id,self)
        return "successfully funded account: %s with %s at %s" % (self.id,amount,transaction_date)

def create_account(account_id=None,location=None):
    global account_object_store
    if account_id and location:
        if is_unique_id(account_id):
            account = Account(account_id,location)
            account_object_store.append(account)
            persist_account_store(account_object_store)
        else:
            return "account exists already"
    else:
        return "not enough info to run"

def check_balance(account_id=None):
    try:
        if account_id:
            return return_account_by_id(account_id).balance()
        else:
            return "not enough info to run"
    except:
        return "An account with id: %s does not exist" % account_id

def send_money(sender_id=None,receiver_id=None,amount=None):
    try:
        if sender_id and receiver_id and amount:
            return return_account_by_id(sender_id).send(receiver_id,amount)
        else:
            return "not enough info to run"
    except:
        return "An account with id: %s does not exist" % account_id

def self_fund_account(account_id=None,amount=None):
    try:
        if account_id and amount:
            return return_account_by_id(account_id).self_fund(amount)
        else:
            return "not enough info to run"
    except:
        return "An account with id: %s does not exist" % account_id

def view_incoming_logs(account_id=None):
    try:
        if account_id:
            return return_account_by_id(account_id).incoming
        else:
            return "not enough info to run"
    except:
        return "An account with id: %s does not exist" % account_id

def view_outgoing_logs(account_id=None):
    try:
        if account_id:
            return return_account_by_id(account_id).outgoing
        else:
            return "not enough info to run"
    except:
        return "An account with id: %s does not exist" % account_id

