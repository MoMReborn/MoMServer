
//-----------------------------------------------------------------------------
// DefaultTrigger is used by the mission editor.  This is also an example
// of trigger methods and callbacks.



//-----------------------------------------------------------------------------

function ZoneTrigger::onEnterTrigger(%this,%trigger,%obj)
{

   Py::ZoneTrigger(%trigger,%obj);
   // This method is called whenever an object enters the %trigger
   // area, the object is passed as %obj.  The default onEnterTrigger
   // method (in the C++ code) invokes the ::onTrigger(%trigger,1) method on
   // every object (whatever it's type) in the same group as the trigger.
   Parent::onEnterTrigger(%this,%trigger,%obj);
}

function ZoneTrigger::onLeaveTrigger(%this,%trigger,%obj)
{
   // This method is called whenever an object leaves the %trigger
   // area, the object is passed as %obj.  The default onLeaveTrigger
   // method (in the C++ code) invokes the ::onTrigger(%trigger,0) method on
   // every object (whatever it's type) in the same group as the trigger.
   Parent::onLeaveTrigger(%this,%trigger,%obj);
}

function ZoneTrigger::onTickTrigger(%this,%trigger)
{
   // This method is called every tickPerioMS, as long as any
   // objects intersect the trigger. The default onTriggerTick
   // method (in the C++ code) invokes the ::onTriggerTick(%trigger) method on
   // every object (whatever it's type) in the same group as the trigger.

   // You can iterate through the objects in the list by using these
   // methods:
   //    %this.getNumObjects();
   //    %this.getObject(n);
   Parent::onTickTrigger(%this,%trigger);
}

