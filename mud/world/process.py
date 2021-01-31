# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

## @defgroup process process
#  @ingroup world
#  @brief The process module contains the Process class which serves as a parent
#         class for actions that are processed incrementally.
#  @{


## @brief Process contains mechanics for incremental processing of actions.
#  @details Process is designed to be serve as a base class.
#  @todo TWS: End and Cancel basically do the same thing.  Is there a need for
#        seperate methods?  Should some process control and throttling be
#        done within the base class? 
class Process:
    
    ## @brief (Long) Count of created Processes.  This value is used to create
    #         identifiers for instances of Processes.  
    processCounter = 1L
    
    
    ## @brief Initialize class.
    #  @param self (Process) The object pointer.
    #  @param src (Mob) The source Mob that created the Process.
    #  @param dst (Mob) The destination Mob that the Process targets.
    def __init__(self, src, dst):
        
        ## @brief (Mob) The source Mob that created the Process.
        self.src = src
        
        ## @brief (Mob) The destination Mob that the Process targets.
        self.dst = dst
        
        ## @brief (Generator) The generator object that will be iteratively
        #         called.  
        self.iter = None
        
        ## @brief (Integer) Delay till next iteration.
        #  @remark This is an optional value that can be used to throttle
        #          iterations.
        self.tickCounter = 0
        
        ## @brief (Integer) Value to which the tickCounter is set when the
        #         tickCounter is satisfied.
        #  @remark This can be used to throttle iterations. 
        self.tickRate = 1
        
        ## @brief (Boolean) Flag indicating this Process has been canceled.
        self.canceled = False
        
        ## @brief (Long) Unique identifier for Processes.
        #  @todo TWS: Maybe Python's id() should be used instead?  Technically
        #        a rollaround is possible, but stastical chances of collision is
        #        low.
        self.pid = Process.processCounter
        
        # Increase the static process counter to prevent process identifier
        # collisions.
        Process.processCounter+=1
        
    
    ## @brief Attaches the Process, adding it to the source's processOut list
    #         and the destination's processIn list.
    #  @param self (Process) The object pointer.
    def globalPush(self):
        
        # Append this Process to the source's processOut list.
        self.src.processesOut.add(self)
        
        # Append this Process to the destination's processIn list.
        self.dst.processesIn.add(self)
    
    
    ## @brief Clears the source of a process.
    #  @param self (Process) The object pointer.    
    #  @deprecated TWS: This looks as if it is never used.  It actually looks
    #              as if it is unsafe to call.  This would cause a process to
    #              remain on a source after an end, cancel, or pop.
    def clearSrc(self):
        self.src = None
        
        
    ## @brief Clears the destination of a process.
    #  @param self (Process) The object pointer.
    #  @deprecated TWS: This looks as if it is never used.  It actually looks
    #              as if it is unsafe to call.  This would cause a process to
    #              remain on a source after an end, cancel, or pop.
    def clearDst(self):
        self.dst = None
        
        
    ## @brief Begins the Process, attaching the process to both the source and
    #         destination, as well as setting the iterative call.
    #  @param self (Process) The object pointer.
    #  @return (Boolean) Returns True if the Process succesfully began.
    #          Otherwise, False.
    #  @todo TWS: Does this need to return a value.  It is never checked, but
    #        it might be helpful.   
    def begin(self):
        
        # Attach this Process to the source and destination.
        self.globalPush()
        
        # Get the generator for this Process.
        self.iter = self.tick()
        
        # Return True to indicate the Process successful began.
        return True
    
        
    ## @brief Tick should be overwritten in subclasses with a generator
    #         function.
    #  @param self (Process) The object pointer.
    def tick(self):
        return False
    
    
    ## @brief Ends a Process.  Detaching the Process from both the source and
    #         destination.
    #  @param self (Process) The object pointer.
    def end(self):
        
        # If this Process has already been canceled, then return early.
        if self.canceled:
            return
        
        # Detach this Process from the source and destination.
        self.globalPop()
        return 
    
     
    ## @brief Cancel the Process, preventing more iterations, and detaching the
    #         Process from both the source and destination.
    #  @param self (Process) The object pointer.   
    def cancel(self):
        
        # If this Process has already been canceled, then return early.
        if self.canceled:
            return 
        
        # Set a flag to indicate this Process has been canceled.
        self.canceled = True
        
        # Destroy this Process' generator object.
        self.iter = None
        
        # Detach this Process from the source and destination.
        self.globalPop()
        
    
    ## @brief Detaches the Process, removing it from the source's processOut
    #         list and the destination's processIn list.
    #  @param self (Process) The object pointer.  
    def globalPop(self):
        
        # If this Process is in the source's processOut list, then remove this
        # Process from the list.
        self.src.processesOut.discard(self)
            
        # If this Process is in the destination's processIn list, then remove
        # this Process from the list.
        self.dst.processesIn.discard(self)
            

## @} # End process group.