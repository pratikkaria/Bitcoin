## Questions

* ordering between processBlocks and processTransactions - which one should go first?
  * There is one dependency between these two - while a block is getting processed, its transactions should not lie unprocessed in the transaction queue
  * So we can try processing transactions first and don't go for blocks processing (until all the transactions are processed)
  * Here, the question is what will be the frequency of incoming transactions? If it's too high, we won't be able to proceed with our blocks processing and other tasks
  * -> we can handle this: if we notice while processing a block that there is/are transaction(s) which need(s) to be present, then we can do transactions processing from here (in chunks) till it satisfies our block and then we move on == this looks as a good approach
* When should we broadcast a transaction? How do we decide the ordering? Take input from file, but how do we know that the dependent transactions are not broadcasted first?
  * -> we can check in our unspntTxOut, if the txn inputs for our new transaction are already there in the pool, then we can go ahead otherwise wait
* We can't go to proof of work until and unless we have finished processing the incoming blocks, right? And after that, once we go into the proof of work, we need to know somehow that a new block has arrived into the blocks queue. In this case, we need to process the block and restart the proof of work. But, once we have completed our proof of work, then we can broadcast the block and only then look for further incoming blocks in queue to process them. In this way, the block(s) that will have common transactions with the block we produced will be rejected.
  * How do we know in the middle of proof of work, that a new block has arrived? 
    * Two options - polling or signals
    * which one to prefer?
* How many transactions should be in the pool, to start doing proof of work or before broadcasting a block? In other words, how many minimum no of transactions a block should have to broadcast it?
* We can have a broadcastTxns instead of broadcast-a-single-txn so that any transaction which can be sent, will be sent - it will not wait for any other transaction to be able to broadcasted
* We can initialize a hard-coded genesis block in the BlockChain() constructor itself
