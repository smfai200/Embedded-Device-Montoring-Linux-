import os


class Finder:
    def __init__(self, *args, **kwargs):
        self.server_name = kwargs['server_name']
        self.password = kwargs['password']
        self.interface_name = kwargs['interface']
        self.main_dict = {}

    def run(self):
        command = ''' sudo iwlist {} scan | grep -ioE 'ssid:"({})"' '''
        result = os.popen(command.format(self.interface_name,self.server_name))
        result = list(result)
        print(result)

        if "Device or resource busy" in result:
                return None
        else:
            ssid_list = [item.lstrip('SSID:').strip('"\n') for item in result]
            print("Successfully get ssids {}".format(str(ssid_list)))

        for name in ssid_list:
            try:
                print("Tring to Connect to: ", name)
                result = self.connection(name)
                print("Successfully connected to {}".format(connect_name))
                
            except Exception as exp:
                print("Couldn't connect to name : {}. {}".format(name, exp))

                    

    def connection(self, name):
        command = '''nmcli d wifi connect "{}" password "{}" iface "{}" '''.format(name,
       self.password,
       self.interface_name)
        os.system(command)
