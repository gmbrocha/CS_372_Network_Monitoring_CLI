# Modified from starter code created by/at
# Author: Bram Lewis
# Availability: https://canvas.oregonstate.edu/courses/1957923/assignments/9654612?module_item_id=24358446

# Future versions will have the ability to add multiple hosts for all services instead of only ping/trace

import threading
import time
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.patch_stdout import patch_stdout
from network_monitoring_tools import ping, traceroute, check_server_http, check_server_https, check_dns_server_status, \
    check_ntp_server, check_udp_port, check_tcp_port
from timestamp_print import timestamped_print
import yaml


def ping_worker(stop_event: threading.Event, services_params: dict, services: dict, interval: int, host: str) -> None:
    """
    Ping service worker that accepts various service parameters from the Thread call to it; will be called for every
    host in the parameter host list; runs until the stop event is set by keyboard interruption; returns None
    """
    while not stop_event.is_set():
        if services["Ping"]:
            timestamped_print("Ping host:", host, "Status (Host/RTT):",
                              ping(host, services_params["Ping"]["ttl"], services_params["Ping"]["timeout"],
                                   services_params["Ping"]["sequence_number"]), "\n")
        time.sleep(interval)


def traceroute_worker(stop_event: threading.Event, services_params: dict, services: dict, interval: int,
                      host: str) -> None:
    """
    Traceroute service worker that accepts various service parameters from the Thread call to it; will be called for
    every host in the services_params host list; runs until the stop event is set by keyboard interruption; returns
    None
    """
    while not stop_event.is_set():
        if services["Traceroute"]:
            timestamped_print("Traceroute host:", host, "Status (Host/RTT):",
                              traceroute(host, services_params["Traceroute"]["max_hops"],
                                         services_params["Traceroute"]["pings_per_hop"],
                                         services_params["Traceroute"]["verbose"]), "\n")
        time.sleep(interval)


def http_worker(stop_event: threading.Event, services_params: dict, services: dict, interval: int) -> None:
    """
    HTTP service monitoring worker that accepts parameters in services_params; accepts the services dict to check if
    worker should be active; runs on the interval set by the user; returns None
    """
    while not stop_event.is_set():
        if services["HTTP"]:
            if services_params["HTTP"]["url"]:
                timestamped_print("HTTP host:", services_params["HTTP"]["url"], "Status (Active/Response Code):",
                                  check_server_http(services_params["HTTP"]["url"]), "\n")
        time.sleep(interval)


def https_worker(stop_event: threading.Event, services_params: dict, services: dict, interval: int) -> None:
    """
    HTTPS service monitoring worker that accepts parameters in services_params; accepts the services dict to check if
    worker should be active; runs on the interval set by the user; returns None
    """
    while not stop_event.is_set():
        if services["HTTPS"]:
            if services_params["HTTPS"]["url"]:
                timestamped_print("HTTPS host:", services_params["HTTPS"]["url"],
                                  "Status (Active/Response Code/Message):",
                                  check_server_https(services_params["HTTPS"]["url"]), "\n")
        time.sleep(interval)


def ntp_worker(stop_event: threading.Event, services_params: dict, services: dict, interval: int) -> None:
    """
    NTP service monitoring worker that accepts parameters in services_params; accepts the services dict to check if
    worker should be active; runs on the interval set by the user; returns None
    """
    while not stop_event.is_set():
        if services["NTP"]:
            if services_params["NTP"]["server"]:
                timestamped_print("NTP host:", services_params["NTP"]["server"], ", Status (Active/Current Datetime):",
                                  check_ntp_server(services_params["NTP"]["server"]), "\n")
        time.sleep(interval)


def dns_worker(stop_event: threading.Event, services_params: dict, services: dict, interval: int) -> None:
    """
    DNS service monitoring worker that accepts parameters in services_params; accepts the services dict to check if
    worker should be active; runs on the interval set by the user; returns None
    """
    while not stop_event.is_set():
        if services["DNS"]:
            if services_params["DNS"]["server"] and services_params["DNS"]["query"] and \
                    services_params["DNS"]["record_type"]:
                timestamped_print("DNS Server:" + f" {services_params['DNS']['server']}" +
                                  ", Status (Active/Addresses for Record Type):",
                                  check_dns_server_status(services_params["DNS"]["server"],
                                                          services_params["DNS"]["query"],
                                                          services_params["DNS"]["record_type"]), "\n")
        time.sleep(interval)


def tcp_worker(stop_event: threading.Event, services_params: dict, services: dict, interval: int) -> None:
    """
    TCP service monitoring worker that accepts parameters in services_params; accepts the services dict to check if
    worker should be active; runs on the interval set by the user; returns None
    """
    while not stop_event.is_set():
        if services["TCP"]:
            if services_params["TCP"]["ip_address"] and services_params["TCP"]["port"]:
                timestamped_print("TCP IP/Port:", services_params["TCP"]["ip_address"], ":",
                                  services_params["TCP"]["port"],
                                  ", Status (Active/Status Message):",
                                  check_tcp_port(services_params["TCP"]["ip_address"],
                                                 int(services_params["TCP"]["port"])), "\n")
        time.sleep(interval)


def udp_worker(stop_event: threading.Event, services_params: dict, services: dict, interval: int) -> None:
    """
    UDP service monitoring worker that accepts parameters in services_params; accepts the services dict to check if
    worker should be active; runs on the interval set by the user; returns None
    """
    while not stop_event.is_set():
        if services["UDP"]:
            if services_params["UDP"]["ip_address"] and services_params["UDP"]["port"] and \
                    services_params["UDP"]["timeout"]:
                timestamped_print("UDP IP/Port:", services_params["UDP"]["ip_address"], ":",
                                  services_params["UDP"]["port"],
                                  ", Status (Active/Status Message/Response):",
                                  check_udp_port(services_params["UDP"]["ip_address"],
                                                 int(services_params["UDP"]["port"]),
                                                 int(services_params["UDP"]["timeout"])), "\n")
        time.sleep(interval)


# Main function
def main() -> None:
    """
    Main function to handle user input through menus; allows for configuration setup and export/import; allows for
    starting/stopping worker monitoring threads; uses prompt-toolkit for handling user input with auto-completion
    and ensures the prompt stays at the bottom of the terminal.
    """
    # Command completer for auto-completion
    # This is where you will add new auto-complete commands
    command_completer: WordCompleter = WordCompleter(['exit'], ignore_case=True)

    # Create a prompt session
    session: PromptSession = PromptSession(completer=command_completer)

    # Variable to control the main loop
    is_running: bool = True

    services_params = {
        "Ping": {"host": ["52.27.33.250"], "ttl": 64, "timeout": 1, "sequence_number": 1, "interval": 5},
        "Traceroute": {"host": ["52.27.33.250"], "max_hops": 50, "pings_per_hop": 1,
                       "verbose": True, "interval": 5},
        "HTTP": {"url": "http://gaia.cs.umass.edu", "interval": 5},
        "HTTPS": {"url": "https://www.google.com", "timeout": 5, "interval": 5},
        "NTP": {"server": "pool.ntp.org", "interval": 5},
        "DNS": {"server": "8.8.8.8", "query": "www.google.com", "record_type": "A", "interval": 5},
        "TCP": {"ip_address": "127.0.0.1", "port": 12345, "interval": 5},
        "UDP": {"ip_address": "127.0.0.1", "port": 12346, "timeout": 3, "interval": 5}
    }

    services = {"Ping": True, "Traceroute": True, "HTTP": True, "HTTPS": True, "ICMP": True, "DNS": True, "NTP": True,
                "TCP": True, "UDP": True}

    try:
        with patch_stdout():
            print("\n ------------------------"
                  "\n | NETWORK MONITOR V0.9 |"
                  "\n ------------------------", flush=True)
            while is_running:

                # MAIN MENU
                print(
                    "\n -------------"
                    "\n | Main Menu |"
                    "\n -------------"
                    "\n\n 1. Configure"
                    "\n 2. Start Monitoring"
                    "\n 3. Exit"
                    "\n")

                user_choice: str = session.prompt("Please enter command or command number : ")

                # main exit conditional, breaks top loop
                if user_choice == "3" or user_choice.lower() == "exit":
                    is_running = False
                    print("")
                    timestamped_print("Shutting down...\n")
                    continue

                while not user_choice.isnumeric() and 0 < int(user_choice) < 5:  # simply validation for menu item
                    user_choice: str = session.prompt("Please enter valid command number: ")

                match user_choice:

                    # CONFIG MENU
                    case "1":
                        # run continuous loops for all sub-menus until user desires to exit back to main
                        is_config: bool = True
                        while is_config:
                            print(
                                "\n -------------------------"
                                "\n | Configuration Options |"
                                "\n -------------------------"
                                "\n\n 1. Load Config"
                                "\n 2. Save Config"
                                "\n 3. Services Enabled/Disabled"
                                "\n 4. Service Parameters"
                                "\n 5. Monitoring Interval"
                                "\n 6. Exit to Main\n")
                            user_choice: str = session.prompt("Please enter a command number: ")

                            if user_choice == "6" or user_choice.lower() == "exit":
                                is_config = False
                                continue

                            while not user_choice.isnumeric() and 0 < int(
                                    user_choice) < 5:  # simply validation for menu item
                                user_choice: str = session.prompt("Please enter valid command number: ")

                            match user_choice:

                                # LOAD CONFIG
                                case "1":
                                    user_input: str = session.prompt(
                                        "\nConfig will be loaded from /config/param_config.yaml and "
                                        "/config/services_config.yaml, proceed? (Y/N or 'exit' to "
                                        "return to config main): ")
                                    if user_input.lower() == "n" or user_input.lower() == "exit":
                                        continue
                                    elif user_input.lower() == "y":
                                        with open("./config/param_config.yaml", "r") as f:
                                            services_params = yaml.safe_load(f)
                                            f.close()
                                        with open("./config/services_config.yaml", "r") as f:
                                            services = yaml.safe_load(f)
                                            f.close()

                                        print("")
                                        timestamped_print("Parameters and services loaded from configuration "
                                                          "files, returning to main config menu.")

                                # SAVE CONFIG
                                case "2":
                                    user_input: str = session.prompt(
                                        "\nSave config to file? (Y/N or 'exit' to return to config main): ")
                                    if user_input.lower() == "n" or user_input.lower() == "exit":
                                        continue
                                    elif user_input.lower() == "y":
                                        with open("./config/param_config.yaml", mode="wt") as f:
                                            yaml.safe_dump(services_params, f)
                                            f.close()
                                        with open("./config/services_config.yaml", mode="wt") as f:
                                            yaml.safe_dump(services, f)
                                            f.close()

                                        print("")
                                        timestamped_print("Parameters and active services saved in /config"
                                                          "(param_config.yaml, services_config.yaml), returning to main"
                                                          "config menu.")

                                # SERVICES ACTIVATION/DEACTIVATION
                                case "3":
                                    print(
                                        "\n -----------------------"
                                        "\n | Monitoring Services |"
                                        "\n -----------------------")
                                    services_edit: bool = True

                                    while services_edit:

                                        print("\nServices available: HTTP, HTTPS, ICMP, DNS, NTP, TCP, UDP")
                                        print("---------------------------------------------------------")
                                        timestamped_print("Current services active: ", end=" ", flush=True)
                                        i = 0
                                        for service in services:
                                            if services[service] is True and i != len(services) - 1:
                                                print(service + ", ", end=" ", flush=True)
                                            elif services[service] is True and i == len(services) - 1:
                                                print(service, flush=True)
                                            i += 1
                                        print("")
                                        user_services: str = session.prompt(
                                            "\nWould you like to edit active services? (Y/N to return to config main): "
                                        )
                                        if user_services.lower() == "y" or user_services.lower() == "yes":
                                            user_service_choice: str = session.prompt("\nPlease enter service which to "
                                                                                      "activate or deactivate (or 'exit'"
                                                                                      " to return to main config menu): "
                                                                                      )
                                            if user_service_choice.lower() == "exit":
                                                break
                                            while user_service_choice.upper() not in services:
                                                user_service_choice: str = session.prompt(
                                                    "\nPlease enter a valid service to activate/deactivate "
                                                    "(or 'exit' to return to main config menu): ")
                                                if user_service_choice.lower() == "exit":
                                                    services_edit = False
                                                    break

                                            services[user_service_choice] = not services[user_service_choice]
                                            print("")
                                            timestamped_print("Service configuration changed.")
                                            timestamped_print("Current services active: ", end=" ", flush=True)
                                            i = 0
                                            for service in services:
                                                if services[service] is True and i != len(services) - 1:
                                                    print(service + ", ", end=" ", flush=True)
                                                elif services[service] is True and i == len(services) - 1:
                                                    print(service + ".", end=" ", flush=True)
                                                i += 1
                                            print("")
                                        else:
                                            services_edit = False

                                    else:
                                        continue

                                # SERVICES PARAMETERS
                                case "4":
                                    print("\n ----------------------"
                                          "\n | Service Parameters |"
                                          "\n ----------------------")

                                    service_nums = ["Ping", "Traceroute", "HTTP", "HTTPS", "NTP", "DNS", "TCP", "UDP"]

                                    params_edit: bool = True
                                    while params_edit:

                                        print("\n Current services and parameters"
                                              "\n -------------------------------")
                                        i = 0
                                        j = 1
                                        for service in services_params:
                                            print(" " + str(j) + ": " + service + ". Parameters:", end=" ")
                                            j += 1
                                            for param in services_params[service]:
                                                i += 1
                                                if i == len(services_params[service]):
                                                    print(param + ": " + str(services_params[service][param]) + ".")
                                                    i = 0
                                                else:
                                                    print(param + ": " + str(services_params[service][param]) + ",",
                                                          end=" ")
                                        print(" 9: Reset to Default Parameters")

                                        user_choice: str = session.prompt(
                                            "\nPlease enter a service number to edit "
                                            "('exit' to return to main config menu): ")

                                        if user_choice.lower() == "exit":
                                            params_edit = False
                                            continue

                                        while not user_choice.isnumeric() and not 0 < int(user_choice) < 10:
                                            user_choice: str = session.prompt(
                                                "\nPlease enter a valid service number "
                                                "('exit' to return to main config): ")
                                            if user_choice.lower() == "exit":
                                                params_edit = False
                                                break
                                        if params_edit is False:
                                            continue

                                        if user_choice == "9":
                                            user_confirm: str = session.prompt("\nReset to default parameters? (Y/N): "
                                                                               )
                                            if user_confirm.lower() == "y":
                                                with open("./config/param_config_default.yaml", "r") as f:
                                                    services_params = yaml.safe_load(f)
                                                print("\nParameters restored to default. "
                                                      "Returning to config main menu.")
                                            continue

                                        print("\n " + service_nums[int(user_choice) - 1] + " parameters:", end=" ")
                                        k = 0
                                        for param in services_params[service_nums[int(user_choice) - 1]]:
                                            if k == len(services_params[service_nums[int(user_choice) - 1]]) - 1:
                                                print(param + ".", flush=True)
                                            else:
                                                print(param + ", ", end=" ")
                                                k += 1
                                        print(" ------------------------------\n")

                                        user_param: str = session.prompt(
                                            "Please type the parameter you wish to change for " +
                                            service_nums[
                                                int(user_choice) - 1] + " ('exit' to return to parameter main menu): ")

                                        if user_param.lower() == "exit":
                                            continue

                                        end_param_edit = False
                                        while user_param not in services_params[service_nums[int(user_choice) - 1]]:
                                            k = 0
                                            print("\n " + service_nums[int(user_choice) - 1] + " parameters:",
                                                  end=" ")
                                            for param in services_params[service_nums[int(user_choice) - 1]]:
                                                if k == len(services_params[service_nums[int(user_choice) - 1]]) - 1:
                                                    print(param + ".", flush=True)
                                                else:
                                                    print(param + ", ", end=" ")
                                                    k += 1
                                            print(" ------------------------------\n")

                                            user_param: str = session.prompt(
                                                "\nPlease enter a valid parameter "
                                                "('exit' to return to parameter main menu): ")

                                            if user_param == "exit":
                                                end_param_edit = True
                                                break

                                        if end_param_edit is True:
                                            continue

                                        if user_param == "host" and user_choice == "1" or user_choice == "2":
                                            user_param_add: str = session.prompt(
                                                "\nPlease enter a hostname or IP to add to the monitoring list: ")
                                            services_params[service_nums[int(user_choice) - 1]]["host"].append(
                                                user_param_add)
                                        else:
                                            user_param_add: str = session.prompt(
                                                "\nPlease enter the new value for the parameter: ")
                                            services_params[service_nums[int(user_choice) - 1]][
                                                user_param] = user_param_add

                                # MONITORING INTERVAL
                                case "5":
                                    print(
                                        "\n -----------------------"
                                        "\n | Monitoring Interval |"
                                        "\n -----------------------\n")

                                    print("\nCurrent monitoring intervals: ")
                                    for service in services_params:
                                        print(service + ": " + str(services_params[service]["interval"]) + "s")
                                    user_service: str = session.prompt(
                                        "\nFor which service would you like to change the interval? "
                                        "('exit' to return to config main menu): ")
                                    if user_service == "exit":
                                        continue

                                    while user_service.upper() not in services_params:
                                        user_service: str = session.prompt(
                                            "\nPlease enter a valid service. "
                                            "('exit' to return to config main menu): ")
                                        if user_interval == "exit":
                                            continue
                                    user_interval: str = session.prompt(
                                        "\nPlease enter a new interval "
                                        "(seconds, 'exit' to return to config main menu): ")
                                    if user_interval == "exit":
                                        continue

                                    while not user_interval.isnumeric():
                                        user_interval: str = session.prompt(
                                            "\nPlease enter a valid interval "
                                            "(seconds, 'exit' to return to config main menu): ")
                                        if user_interval == "exit":
                                            continue

                                    services_params[user_service.upper()] = int(user_interval)

                                    print("\n" + user_service + " interval updated to" + user_interval + "s.\n")

                    # START MONITORING
                    case "2":
                        # Event to signal the worker thread to stop
                        stop_event: threading.Event = threading.Event()

                        # list to keep track of workers to call .join() on later
                        threads = []

                        # Create and start the worker thread
                        w_one: threading.Thread = threading.Thread(target=http_worker, args=(stop_event,),
                                                                   kwargs={'services_params': services_params,
                                                                           "services": services,
                                                                           "interval": services_params["HTTP"][
                                                                               "interval"]})
                        w_one.start()
                        threads.append(w_one)

                        w_two: threading.Thread = threading.Thread(target=https_worker, args=(stop_event,),
                                                                   kwargs={'services_params': services_params,
                                                                           "services": services,
                                                                           "interval": services_params["HTTPS"][
                                                                               "interval"]})
                        w_two.start()
                        threads.append(w_two)

                        w_three: threading.Thread = threading.Thread(target=ntp_worker, args=(stop_event,),
                                                                     kwargs={'services_params': services_params,
                                                                             "services": services,
                                                                             "interval": services_params["HTTPS"][
                                                                                 "interval"]})
                        w_three.start()
                        threads.append(w_three)

                        w_four: threading.Thread = threading.Thread(target=dns_worker, args=(stop_event,),
                                                                    kwargs={'services_params': services_params,
                                                                            "services": services,
                                                                            "interval": services_params["HTTPS"][
                                                                                "interval"]})
                        w_four.start()
                        threads.append(w_four)

                        w_five: threading.Thread = threading.Thread(target=tcp_worker, args=(stop_event,),
                                                                    kwargs={'services_params': services_params,
                                                                            "services": services,
                                                                            "interval": services_params["HTTPS"][
                                                                                "interval"]})
                        w_five.start()
                        threads.append(w_five)

                        w_six: threading.Thread = threading.Thread(target=udp_worker, args=(stop_event,),
                                                                   kwargs={'services_params': services_params,
                                                                           "services": services,
                                                                           "interval": services_params["HTTPS"][
                                                                               "interval"]})
                        w_six.start()
                        threads.append(w_six)

                        ping_hosts = services_params["Ping"]["host"]
                        num_hosts = len(ping_hosts)
                        for i in range(num_hosts):
                            w = threading.Thread(target=ping_worker, args=(stop_event,), kwargs={
                                "services_params": services_params, "services": services,
                                "interval": services_params["Ping"]["interval"], "host": ping_hosts[i]})
                            w.start()
                            threads.append(w)
                        trace_hosts = services_params["Traceroute"]["host"]
                        num_hosts = len(trace_hosts)
                        for i in range(num_hosts):
                            w = threading.Thread(target=traceroute_worker, args=(stop_event,), kwargs={
                                "services_params": services_params, "services": services,
                                "interval": services_params["Traceroute"]["interval"], "host": trace_hosts[i]})
                            w.start()
                            threads.append(w)

                        print("(Ctrl + C to end monitoring)\n")

                        try:
                            while True:
                                time.sleep(.1)

                        except KeyboardInterrupt:
                            print("Attempting to close monitoring threads...")
                            stop_event.set()

                            for t in threads:
                                t.join()

                        finally:
                            continue
    finally:
        return


if __name__ == "__main__":
    main()
