import copy
# 1
transtable = []
locktable = []
waitingtable = []
inputlist = []

T_ACTIVE = 'ACTIVE'
T_BLOCKED = 'BLOCKED'
T_WAITING = 'WAITING'
T_ABORTED = 'ABORTED'
T_COMMITTED = 'COMMITTED'

L_READLOCK = 'READ(SHARE) LOCKED'
L_WRITELOCK = 'WRITE(EXCLUSIVE) LOCKED'

# 2
class transitem():
    def __init__(self, id, timestamp, state):
        print('New Transaction Item: id(' + str(id) + ') timestamp(' + str(timestamp) + ') state(' + str(state) +')')
        self.id = id
        self.timestamp = timestamp
        self.state = state
        self.lockeditems = []
        self.blockedoperations = []

    def setState(self, state):
        print('Changed State of Transaction ' + self.id + ' to ' + state)
        self.state = state

    def setBlockedOperation(self, operation):
        print('Add operation ' + operation + ' to Blocked Array under Transaction ' + self.id)
        self.blockedoperations.append(operation)

    def setLockedItem(self, item):
        print('Add Item ' + item + ' to Locked Items Array under Transaction ' + self.id)        
        self.lockeditems.append(item)    

# 3
class lockitem:
    def __init__(self, name, state, transid):
        print('New Lock Item: item name(' + str(name) + ') Transaction(' + str(transid) + ') state(' + str(state) +')')
        self.name = name
        self.state = state
        self.holdingtrans = []
        self.holdingtrans.append(transid)
        self.waitingtrans = []

    def setState(self, state):
        print('Changed State of Locked Item ' + self.name + ' to ' + state)
        self.state = state        
        
    def setheldtrans(self, transid):
        print('Add Transaction ' + transid + ' to Holding Transaction Array under Locked Item ' + self.name)
        self.holdingtrans.append(transid)

    def setWaitingTransaction(self, transid):
        print('Add Transaction ' + transid + ' to Waiting Transaction Array under Locked Item ' + self.name)
        self.waitingtrans.append(transid)

def ReleaseFreeableItems():
    print ("Check All Transactions and Release Items if freeable")
    for trans in waitingtable:
        if trans.state == T_ABORTED:
            waitingtable.remove(trans)
        else:
            temp = copy.deepcopy(trans.blockedoperations)
            for bOp in trans.blockedoperations:
                trans.setState(T_ACTIVE)
                print ("Attempt Operation " + bOp)
                if trans.state != T_WAITING:
                    temp.remove(bOp)
            trans.bOp = temp
            if len(trans.bOp) == 0:
                waitingtable.remove(trans)

def WWMechanism(reqtrans, heldtrans, lockitem, operation):
    if reqtrans.timestamp < heldtrans.timestamp:
        heldtrans.setState(T_ABORTED)
        print ("Aborting Transaction " + heldtrans.id)
        reqtrans.setState(T_WAITING)
        reqtrans.setBlockedOperation(operation)
        waitingtable.append(reqtrans)
        unlock(heldtrans.id)
    else:
        reqtrans.setState(T_WAITING)
        print ("Set State Blocked to Transaction " + reqtrans.id)
            
def getTransID(transid):
    for trans in transtable:
        if trans.id == transid:
            return trans
        
def unlock(transid):
    print ("Unlock Items Held by Transaction " + transid)
    for trans in transtable:
        if trans.id == transid:
            for lock in trans.lockeditems:
                for resource in locktable:
                    if resource.name == lock:
                        if len(resource.holdingtrans) == 1:
                            locktable.remove(
                                resource)
                        else:
                            resource.holdingtrans.remove(
                                transid)
    ReleaseFreeableItems()
            
# 4        
def simulate():
    for line in inputlist:
        print('======================================\nInput Operation: ' + line)
        # 5
        if line[0] == 'b':
            transid = line[1]
            print('Begin Transaction ' + transid)
            timestamp = len(transtable) + 1
            transtable.append(transitem(transid, timestamp, T_ACTIVE))
        # 12
        if line[0] == 'e':
            transid = line[1]
            print('End Transaction ' + transid)
            for trans in transtable:
                if trans.id == transid and trans.state != T_ABORTED:
                    trans.setState(T_COMMITTED)
            unlock(transid)            
        # 6
        elif line[0] == 'r':
            transid = line[1]
            itemid = 'A'
            if line[3] == '(':
                itemid = line[4]
            else:
                itemid = line[3]
            
            alreadyFlag = False
            locklen = len(locktable)
            if locklen > 0:
                for i in range(0, locklen):
                    if locktable[i].name == itemid:
                        alreadyFlag = True
                        if locktable[i].state == L_WRITELOCK:
                            print("Conflict Write Lock: " + itemid + " is already Write Locked by Transaction " + transid)
                            print("For deadlock prevention: Wound-Wait Mechanism")
                            
                            WWMechanism(getTransID(transid),
                                      getTransID(locktable[i].holdingtrans[0]), locktable[i], line)                            
                                      
                        elif locktable[i].state == L_READLOCK:
                            locktable[i].setheldtrans(transid)
                            getTransID(transid).setLockedItem(itemid)  
                            print (itemid + " is already Non-Conflicting Read-Lock, so adding it to Transaction " + locktable[i].holdingtrans[0]) 
                if alreadyFlag == False:
                    locktable.append(lockitem(itemid, L_READLOCK, transid))
                    getTransID(transid).setLockedItem(itemid)
                    print ("Set item " + itemid + " under read-lock by transaction " + transid)                    
            else:
                locktable.append(lockitem(itemid, L_READLOCK, transid))
                
                getTransID(transid).setLockedItem(itemid)
                print ("Set item " + itemid + " under read-lock by transaction " + locktable[0].holdingtrans[0])
                
        # 7
        elif line[0] == 'w':
            transid = line[1]
            
            itemid = 'A'
            if line[3] == '(':
                itemid = line[4]
            else:     
                itemid = line[3]
                
            alreadyFlag = False
            locklen = len(locktable)
            
            if locklen != 0:
                for i in range(0, locklen):
                    if locktable[i].name == itemid:
                        alreadyFlag = True
                        
                        if locktable[i].state == L_READLOCK:
                            
                            if len(locktable[i].holdingtrans) == 1:
                                if locktable[i].holdingtrans[0] == transid:
                                    locktable[i].setState(L_WRITELOCK)
                                    print('Item ' + itemid + ' is readLock by the same Transaction ' + transid + ', upgrade it to Write-Lock')
                                else:
                                    print('Item ' + itemid + ' is multiple read-lock')
                                    print("For deadlock prevention: Wound-Wait Mechanism")
                                    WWMechanism(getTransID(transid),getTransID(locktable[i].holdingtrans[0]), locktable[i],line)
                            else:
                                holdCnt = 0
                                
                                for lckitem in locktable:
                                    if lckitem.name == itemid:
                                        for holditem in lckitem.holdingtrans:
                                            if holditem == transid:
                                                holdCnt += 1
                                                
                                print("For deadlock prevention: Wound-Wait Mechanism")
                                WWMechanism(getTransID(transid),getTransID(locktable[i].holdingtrans[holdCnt]), locktable[i],line)                                
  
                        elif locktable[i].state == L_WRITELOCK:
                            print("Conflict Write Lock: " + itemid + " is already Write Locked by Transaction " + transid)
                            print("For deadlock prevention: Wound-Wait Mechanism")                 
                            
                            WWMechanism(getTransID(transid),getTransID(locktable[i].holdingtrans[0]), locktable[i], line)
                            
                if alreadyFlag == False:
                    locktable.append(lockitem(itemid, L_WRITELOCK, transid))
                    getTransID(transid).setLockedItem(itemid)
                    print ("Set item " + itemid + " under write-lock by transaction " + locktable[0].holdingtrans[0])   
            else:
                locktable.append(lockitem(itemid, L_WRITELOCK, transid))
                getTransID(transid).setLockedItem(itemid)  
       
def main():
    filename = input('Please input File Name: ')
    infile = open(filename, 'r')
    for line in infile:
        inputlist.append(line.strip())
    simulate()
    infile.close()
main()