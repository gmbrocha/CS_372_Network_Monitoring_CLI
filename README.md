This app allows for network monitoring via multiple services (Ping, Traceroute, HTTP, HTTPS, NTP, DNS, TCP, UDP) which
can all be configured individually. The CLI presents easy to follow menus to configure and run the monitoring 
application.

Once configured, and network monitoring is started via option 2 in the main menu, it will continue to monitor will the
current configuration until interrupted with a keyboard interrupt (Ctrl + c) which will return the user to the main
menu.

Configuration can be loaded or saved (and restored to defaults) to/from .yaml files within the /config folder. Default
configuration will load with app restart. The configuration files can be edited manually, and loaded via the config
menu (option 1) to be run with the current session; however, upon restart configuration will return to default (and 
will need to be reloaded to the custom config if desired). Configuration changed within the CLI can be persisted to the 
.yaml config files via config menu (option 2).

Configuration menu option 3 will activate or deactivate services to monitor. All services available as well as the 
current active services will display upon entering the sub-menu. To activate a deactivated service, simply enter the 
service name. To deactivate, enter the service name in the same menu once more.

Service parameters can be changed via option 4 in the config menu. Once in the sub-menu, enter the number of the service
desired to change, followed by the name of the parameter. Then, enter the value desired for the parameter and press
enter. The updated parameter will then display in the re-display of the sub-menu. Option 9 will reset all parameters
to default. Type 'exit' to return to the config main menu.

Monitoring intervals for each service can be changed via option 5 in the config menu. Each can be changed independently.

