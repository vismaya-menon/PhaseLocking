BRIEF DESCRIPTION- 
We check for the inputs from the input file.
Before executing any operation on a transaction, we’ll need to check it’s transaction state
If active, check for any locks on locktable.
If no lock, assign lock to the data item and update the locktable
If write lock, then the transaction has to wait (blocked)
If read lock -
Same transaction, then upgrade to write lock
Different transaction, then share the read lock with the current transaction 
If blocked, 
Item is locked, then add the transaction id to the waiting list
Item is not locked, change state to active and update transaction and lock tables.
On encountering ‘b’, create a transaction record in the transaction table with transaction ID and Increment timestamp.


On encountering ‘r’:
If no locks: transaction acquires a read lock on the data item and updates locktable
If nonconflicting lock (readlock by another transaction): the data item will be read/shared locked and updates locktable
If conflicting (write) lock: wound-wait algorithm is used to determine whether to abort the previous transaction or to put the current transaction in waiting, and accordingly updated transaction table.
On encountering ‘w’:
If no locks: transaction acquires a write lock on the data item and updates locktable
If nonconflicting lock (readlock by same transaction): the data item will be upgraded to write lock and updates locktable
If conflicting lock (write or read lock by another transaction): wound-wait algorithm is used to determine whether to abort the previous transaction or to put the current transaction in waiting, and accordingly updated transaction table.
If end is encountered then we will update the transaction table, we need to check the status of the transaction before ending the transaction.
If abort is encountered then we will release all the locks and update the lock table. The state is changed to aborted in the transaction table. After aborting the transaction, the operations of the transaction is ignored.
If commit is encountered then we release all the locks and change transaction state to commit and update the state in transaction table.

