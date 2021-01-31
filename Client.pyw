from mud_ext.gamesettings import override_ip_addresses
override_ip_addresses()

from client import main

import pytge
oldInit = pytge.Init


def Init(*args, **kwargs):
    oldInit(*args, **kwargs)

    # After initialisation patch the masterGui so that non-PG servers are also shown
    from mud.client.gui import masterGui
    masterGui.PyOnPremiumServers()


pytge.Init = Init


if __name__ == '__main__':
    main()