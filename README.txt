STEPS FOR RUNNING WIREGUARD IN KUBERNETES

0)
Need Pi-Hole server setup.
Need domain name, with dynamic DNS setup to point to your router.
Need router configured to forward port 51820 to a LoadBalancer IP that you are
using for the Wireguard service. (I think you can hard code one in wireguard.yaml
and use that. I just started it once and used the external IP in my router config.
Install poetry on system.
Install python (3.13 currently).
Install wireguard client app on each client device.
Run "poetry install" and then "poetry shell" to provide the needed packages
and setup the virtual environment.


1)
Do "brew install wireguard-tools" on Mac, so have wireguard tools to create keys.


2)
Create keys for each client device and the server using the command:

    python create-device.py NAME INDEX#

where NAME will be "server" for the server, and the INDEX# will be "1". For the
other clients, pick unique numbers...

    python create-device.py foo 4
    python create-device.py bar 6
    ...

This will create an .ini file in the data sub-directory, for each device
created. The file has the private and public keys generated and the index
number you provided. For example:

data/foo.ini
    [DEFAULT]
    pvt_key = aB6hgJEj9s98n/wEHC4IDCI/FoNAuqb1RKTHfK1cpmw=
    pub_key = OSt95hvwdKwCZ+9JC7ZNArKtpE9LOpRSVT2v40rqdkw=
    index = 4


3)
Create a wireguard.ini file that has the following contents (you can use the
wireguard.ini.sample):

    [DEFAULT]
    subnet = #.#.#
    external_ip = A_DOMAIN_NAME_OR_IP
    dns = CLUSTER_IP_OF_PIHOLE_UDP_SERVICE
    clients = NAMES,OF,CLIENT,DEVICES

Where the subnet is the three of four parts fo IP address for the tunnel IPs
used by the server and clients. For example, if you use "10.10.10", then the
server will be 10.10.10.1, and the client foo would be 10.10.10.4, and bar
would be 10.10.10.6.

For the external IP, I use the domain name that I registered and has an IP
via the dynamic DNS service I use, to point to my router. If you happen to
have a static IP on the internet (rare), you could use that.

For DNS, we want the cluster IP for the PI-Hole UDP service (not the TCP
service).

The clients value is a comma separate list of the client names defined in
step 2 (e.g. foo,bar).


4)
Create the wireguard-secrets.yaml, client config files, and client QR codes
by running:

    python build.py

This will use the .ini files and information in wireguard.ini to create a
YAML file with secrets that will be used by the Wireguard pod for the
server.

It will also create .conf and .png files in the data sub-directory for
each of the clients. From the Wireguard client app on each device, You can
load the .conf file or read the QR code.

5)
Apply the data/wireguard-secrets.yaml and then the wireguard.yaml to start up
the Wireguard server. Check that the pod is running, You can run the
following to exec into pod:

    ./exec-into-pod

Then, run "wg show" to see setup.


6)
On each client load the corresponding .conf file or scan the QR code, and
then activate the tunnel. Verify you can access web sites and that traffic
is (only) going through the tunnel. You should also have the benefit of AD
blocking due to PI-Hole be used for DNS.


CHANGING THE CONFIGURATION
You can create more devices, delete devices, update the wirequard.ini file
with the active devices, run build.py to generate a new secret file, apply
the data./wireguard-secrets.yaml (and wireguard.yaml, if you change other
items), and then run ./delete-pod to stop the running pod and cause a new
pod to be started, using the updated generated secrets.

For any new clients, you can laod the .conf file or read the corresponding
QR code to prepare them.

The .ini, .conf, and QR files for delete clients can be removed, and the
clients can then be be removed from the clients key in wireguard.ini.

Keep in mind that build.py only checks the uniqueness of indexes for clients
that are in the clients key of wireguard.ini. If you create a client with
an index, remove the client from the list of clients, create a new client
with the same index and add it to the clients key, and then later try to
add the original client to the clients list too, the second client in the
list with the same index will be ignored.

You can avoid this by always making sure to use unique indexes for each
client defined.
