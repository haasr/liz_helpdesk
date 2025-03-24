class TicketItemChoices:
    # Network related items
    NETWORK_CHOICES = [
        ('connectivity', 'Internet/Network Connectivity'),
        ('wifi', 'WiFi Issues'),
        ('ethernet', 'Ethernet Connection'),
        ('vpn', 'VPN Access'),
        ('router', 'Router/Switch Issues'),
        ('performance', 'Network Performance'),
        ('other', 'Other Network Issue')
    ]

    # Workstation related items
    WORKSTATION_CHOICES = [
        ('setup', 'New Computer Setup'),
        ('hardware', 'Hardware Issues'),
        ('remote_desktop', 'Remote Desktop'),
        ('makemeadmin', 'MakeMeAdmin Access'),
        ('monitors', 'Monitor/Display Issues'),
        ('peripherals', 'Keyboard/Mouse/Peripherals'),
        ('other', 'Other Workstation Issue')
    ]

    # Server related items
    SERVER_CHOICES = [
        ('deploy', 'Server Deployment'),
        ('access', 'Server Access'),
        ('maintenance', 'Server Maintenance'),
        ('backup', 'Backup Issues'),
        ('performance', 'Performance Issues'),
        ('storage', 'Storage/Space Issues'),
        ('other', 'Other Server Issue')
    ]

    # Printer related items
    PRINTER_CHOICES = [
        ('connect', 'Printer Connection'),
        ('install', 'Printer Installation'),
        ('error', 'Printer Errors'),
        ('supplies', 'Printer Supplies'),
        ('quality', 'Print Quality Issues'),
        ('other', 'Other Printer Issue')
    ]

    # Software related items
    SOFTWARE_CHOICES = [
        ('install', 'Software Installation'),
        ('update', 'Software Updates'),
        ('license', 'License Management'),
        ('config', 'Software Configuration'),
        ('compatibility', 'Compatibility Issues'),
        ('other', 'Other Software Issue'),
    ]

    # Account related items
    ACCOUNT_CHOICES = [
        ('access', 'Account Access'),
        ('permissions', 'Permission Issues'),
        ('password', 'Password Reset'),
        ('creation', 'Account Creation'),
        ('software_access', 'Software Access Rights'),
        ('other', 'Other Account Issue')
    ]

    LAB_CHOICES = [
        ('instructor_ws', 'Instructor Workstation'),
        ('instructor_periph', 'Instructor Peripherals'),
        ('projector', 'Projector'),
        ('av_equipment', 'A/V Equipment (Control Panel, Microphone)'),
        ('lab_computer', 'Lab Computer'),
        ('lab_periph', 'Lab Peripherals'),
        ('other', 'Other Lab Issue')
    ]

    # Map subtypes to their respective items
    SUBTYPE_TO_ITEMS = {
        'NET': NETWORK_CHOICES,
        'WRK': WORKSTATION_CHOICES,
        'SRV': SERVER_CHOICES,
        'PRT': PRINTER_CHOICES,
        'SFT': SOFTWARE_CHOICES,
        'ACC': ACCOUNT_CHOICES,
        'LAB': LAB_CHOICES,
    }

    ALL_ITEM_CHOICES = NETWORK_CHOICES + WORKSTATION_CHOICES + SERVER_CHOICES + PRINTER_CHOICES + SOFTWARE_CHOICES + ACCOUNT_CHOICES + LAB_CHOICES

