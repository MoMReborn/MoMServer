

function LaunchProjectile(%src, %tgt, %pos,%datablock, %vel)
{
    %p = new (Projectile)() {
    dataBlock        = %datablock;
    initialVelocity  = %vel;
    initialPosition  = %pos;
    sourceObject     = %src;
    sourceSlot       = -1;
    client           = %src.client;
    target           = %tgt;
    };
    MissionCleanup.add(%p);
    
    return %p;
}
