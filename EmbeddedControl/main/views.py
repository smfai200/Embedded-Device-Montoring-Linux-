# The MIT License (MIT)
#
# Copyright (c) 2014 Florian Neagu - michaelneagu@gmail.com - https://github.com/k3oni/
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import platform
import os
import multiprocessing
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
import json
from django.http import HttpResponse
from pydash.settings import TIME_JS_REFRESH, TIME_JS_REFRESH_LONG, TIME_JS_REFRESH_NET, VERSION
from main.filehandler import DocumentForm
from main.models import Document
from django.core.urlresolvers import reverse

time_refresh = TIME_JS_REFRESH
time_refresh_long = TIME_JS_REFRESH_LONG
time_refresh_net = TIME_JS_REFRESH_NET
version = VERSION

def fileupload(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('main.views.getall'))
    else:
        form = DocumentForm() # A empty, unbound form

    documents = Document.objects.all()
    docs = []
    
    for doc in documents:
        obj = [doc.docfile.name.split("/")[-1],doc.docfile.url,doc.docfile.name.split('/')[-4],doc.docfile.name.split('/')[-3],doc.docfile.name.split('/')[-2]]
        docs.append(obj)

    data = json.dumps(docs)
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(data)
    return response

@login_required(login_url='/login/')
def index(request):
    """

    Index page.

    """
    return HttpResponseRedirect('/main')


def chunks(get, n):
    return [get[i:i + n] for i in range(0, len(get), n)]


def get_uptime():
    """
    Get uptime
    """
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_time = str(timedelta(seconds=uptime_seconds))
            data = uptime_time.split('.', 1)[0]

    except Exception as err:
        data = str(err)

    return data


def get_ipaddress():
    """
    Get the IP Address
    """
    data = []
    try:
        eth = os.popen("ip addr | grep LOWER_UP | awk '{print $2}'")
        iface = eth.read().strip().replace(':', '').split('\n')
        eth.close()
        del iface[0]

        for i in iface:
            pipe = os.popen("ip addr show " + i + "| awk '{if ($2 == \"forever\"){!$2} else {print $2}}'")
            data1 = pipe.read().strip().split('\n')
            pipe.close()
            if len(data1) == 2:
                data1.append('unavailable')
            if len(data1) == 3:
                data1.append('unavailable')
            data1[0] = i
            data.append(data1)

        ips = {'interface': iface, 'itfip': data}

        data = ips

    except Exception as err:
        data = str(err)

    return data


def get_cpus():
    """
    Get the number of CPUs and model/type
    """
    try:
        pipe = os.popen("cat /proc/cpuinfo |" + "grep 'model name'")
        data = pipe.read().strip().split(':')[-1]
        pipe.close()

        if not data:
            pipe = os.popen("cat /proc/cpuinfo |" + "grep 'Processor'")
            data = pipe.read().strip().split(':')[-1]
            pipe.close()

        cpus = multiprocessing.cpu_count()

        data = {'cpus': cpus, 'type': data}

    except Exception as err:
        data = str(err)

    return data


def get_users():
    """
    Get the current logged in users
    """
    try:
        pipe = os.popen("who |" + "awk '{print $1, $2, $6}'")
        data = pipe.read().strip().split('\n')
        pipe.close()

        if data == [""]:
            data = None
        else:
            data = [i.split(None, 3) for i in data]

    except Exception as err:
        data = str(err)

    return data


def get_traffic(request):
    """
    Get the traffic for the specified interface
    """
    try:
        pipe = os.popen("cat /proc/net/dev |" + "grep " + request + "| awk '{print $1, $9}'")
        data = pipe.read().strip().split(':', 1)[-1]
        pipe.close()

        if not data[0].isdigit():
            pipe = os.popen("cat /proc/net/dev |" + "grep " + request + "| awk '{print $2, $10}'")
            data = pipe.read().strip().split(':', 1)[-1]
            pipe.close()

        data = data.split()

        traffic_in = int(data[0])
        traffic_out = int(data[1])

        all_traffic = {'traffic_in': traffic_in, 'traffic_out': traffic_out}

        data = all_traffic

    except Exception as err:
        data = str(err)

    return data


def get_platform():
    """
    Get the OS name, hostname and kernel
    """
    try:
        osname = " ".join(platform.linux_distribution())
        uname = platform.uname()

        if osname == '  ':
            osname = uname[0]

        data = {'osname': osname, 'hostname': uname[1], 'kernel': uname[2]}

    except Exception as err:
        data = str(err)

    return data


def get_disk():
    """
    Get disk usage
    """
    try:
        pipe = os.popen("df -Ph | " + "grep -v Filesystem | " + "awk '{print $1, $2, $3, $4, $5, $6}'")
        data = pipe.read().strip().split('\n')
        pipe.close()

        data = [i.split(None, 6) for i in data]

    except Exception as err:
        data = str(err)

    return data


def get_disk_rw():
    """
    Get the disk reads and writes
    """
    try:
        pipe = os.popen("cat /proc/partitions | grep -v 'major' | awk '{print $4}'")
        data = pipe.read().strip().split('\n')
        pipe.close()

        rws = []
        for i in data:
            if i.isalpha():
                pipe = os.popen("cat /proc/diskstats | grep -w '" + i + "'|awk '{print $4, $8}'")
                rw = pipe.read().strip().split()
                pipe.close()

                rws.append([i, rw[0], rw[1]])

        if not rws:
            pipe = os.popen("cat /proc/diskstats | grep -w '" + data[0] + "'|awk '{print $4, $8}'")
            rw = pipe.read().strip().split()
            pipe.close()

            rws.append([data[0], rw[0], rw[1]])

        data = rws

    except Exception as err:
        data = str(err)

    return data


def get_mem():
    """
    Get memory usage
    """
    try:
        pipe = os.popen(
            "free -tm | " + "grep 'Mem' | " + "awk '{print $2,$4,$6,$7}'")
        data = pipe.read().strip().split()
        pipe.close()

        allmem = int(data[0])
        freemem = int(data[1])
        buffers = int(data[2])
        cachedmem = int(data[3])

        # Memory in buffers + cached is actually available, so we count it
        # as free. See http://www.linuxatemyram.com/ for details
        freemem += buffers + cachedmem

        percent = (100 - ((freemem * 100) / allmem))
        usage = (allmem - freemem)

        mem_usage = {'usage': usage, 'buffers': buffers, 'cached': cachedmem, 'free': freemem, 'percent': percent}

        data = mem_usage

    except Exception as err:
        data = str(err)

    return data


def get_cpu_usage():
    """
    Get the CPU usage and running processes
    """
    try:
        pipe = os.popen("ps aux --sort -%cpu,-rss")
        data = pipe.read().strip().split('\n')
        pipe.close()

        usage = [i.split(None, 10) for i in data]
        del usage[0]

        total_usage = []

        for element in usage:
            usage_cpu = element[2]
            total_usage.append(usage_cpu)

        total_usage = sum(float(i) for i in total_usage)

        total_free = ((100 * int(get_cpus()['cpus'])) - float(total_usage))

        cpu_used = {'free': total_free, 'used': float(total_usage), 'all': usage}

        data = cpu_used

    except Exception as err:
        data = str(err)

    return data


def get_load():
    """
    Get load average
    """
    try:
        data = os.getloadavg()[0]
    except Exception as err:
        data = str(err)
    
    return data


def get_netstat():
    """
    Get ports and applications
    """
    try:
        pipe = os.popen(
            "ss -tnp | grep ESTAB | awk '{print $4, $5}'| sed 's/::ffff://g' | awk -F: '{print $1, $2}' "
            "| awk 'NF > 0' | sort -n | uniq -c")
        data = pipe.read().strip().split('\n')
        pipe.close()

        data = [i.split(None, 4) for i in data]

    except Exception as err:
        data = str(err)

    return data

from wifi import Cell, Scheme
from django.utils import simplejson

def Get_Interfaces_Network():
    import os
    interfaces = os.listdir('/sys/class/net/')
    return interfaces

def Get_Wifi_Networks_Basic():
    interfaces = Get_Interfaces_Network()
    All_Networks = {"interfaces":interfaces,"Networks":[]}
    for singleinterface in interfaces:
            try:
                all_networks = Cell.all(singleinterface)
                All_Networks['Networks'] = all_networks
            except:
                pass  
    return All_Networks['Networks']

# class Wifi_Network():
#     def __init__(self):
#         self.ssid = ""
#         self.signal = ""
#         self.quality = ""
#         self.frequency = ""
#         self.bitrates = ""
#         self.encrypted = ""
#         self.channel = ""
#         self.address = ""
#         self.mode= ""

#     def toDict():


def Get_Wifi_Networks(ab):
    interfaces = Get_Interfaces_Network()
    All_Networks = {"interfaces":interfaces,"Networks":[]}
    for singleinterface in interfaces:
            try:
                all_networks = Cell.all(singleinterface)
                
                for network in all_networks:
                    newdict = [network.ssid,network.signal,network.quality,network.frequency,network.bitrates[0],network.encrypted,network.channel,network.address,network.mode]
                    All_Networks['Networks'].append(newdict)
            except:
                pass  

    data = json.dumps(All_Networks['Networks'])
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(data)
    return response

from wificonnector import Finder 
import time
from subprocess import check_output
def Connect_to_wifi(ssid,password):
    
    server_name = ssid
    interface = Get_Interfaces_Network()
    for inter_face in interface:
        if("w" in inter_face):
            interface = inter_face
    F = Finder(server_name=server_name,
               password=password,
               interface=interface)
    F.run()

    time.sleep(1)
    wifi_ip = check_output(['hostname', '-I'])
    print(wifi_ip)
    if(len(wifi_ip) > 2):
        return True
    else:
        return False

class FileData():
    def __init__(self):
        self.FileName = ""
        self.FileUrl = ""
        self.Year = ""
        self.Month = ""
        self.Day = ""

@login_required(login_url='/login/')
def getall(request):
    if(request.method == "POST"):
        print("Post Active")
        ssid = request.POST.get('ssid','')
        password = request.POST.get('password','')
        result = Connect_to_wifi(ssid,password)
        print("Result is:", result)
        return render_to_response('main.html', {'result':result,
                                                'time_refresh': time_refresh,
                                                'time_refresh_long': time_refresh_long,
                                                'time_refresh_net': time_refresh_net,
                                                'version': version}, context_instance=RequestContext(request))
    else:
        result = False
        print("Get Active")

        form = DocumentForm() # A empty, unbound form

        # Render list page with the documents and the form
        return render_to_response('main.html', {'form': form,
                                                'result':result,
                                                'time_refresh': time_refresh,
                                                'time_refresh_long': time_refresh_long,
                                                'time_refresh_net': time_refresh_net,
                                                'version': version}, context_instance=RequestContext(request))
