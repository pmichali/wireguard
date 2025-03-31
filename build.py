import subprocess
import configparser

from jinja2 import Environment, FileSystemLoader


def get_server_info():
    """Obtain all the configuration settings for the server and keys"""
    config = configparser.ConfigParser()
    config.read('wireguard.ini')
    server = {
        'subnet': config['DEFAULT']['subnet'],
        'external_ip': config['DEFAULT']['external_ip'],
        'dns' : config['DEFAULT']['dns'],
        'clients': config['DEFAULT']['clients'].split(','),
    }
    config.read('data/server.ini')
    server.update(
        {
            'pub_key': config['DEFAULT']['pub_key'],
            'pvt_key': config['DEFAULT']['pvt_key'],
            'index': config['DEFAULT']['index'],
        }
    )
    print("Read server info")
    return server


def is_duplicate_index(i, clients):
    """See if index in client already."""
    indexes = [c['index'] for c in clients.values()]
    return i in indexes


def get_clients_info(clients):
    """Obtain all the info for clients and ensure unique IDs."""
    config = configparser.ConfigParser()
    all_clients = {}
    for client in clients:
        config.read(f'data/{client}.ini')
        if client in all_clients.keys():
            print(f"WARNING! Ignoring client {client} as already have entry\n")
            continue
        i = config['DEFAULT']['index']
        if is_duplicate_index(i, all_clients):
            print(f"WARNING! Ingnoring client {client} as index {i} is in use\n")
            continue
        new_client = {
            'name': client,
            'pub_key': config['DEFAULT']['pub_key'],
            'pvt_key': config['DEFAULT']['pvt_key'],
            'index': i,
        }
        all_clients[client] = new_client
        print(f"Read client '{client}' info")
    return all_clients


def make_secrets(server, clients):
    """Build up a secrets YAML for the server."""
    # Create a Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))
    server_template = env.get_template('secret.tmpl')
    with open("data/wireguard-secret.yaml", "w") as f:
        f.write(server_template.render(server=server, clients=clients))
    print("\nGenerated wireguard-secret.yaml with server config\n")


def make_configs(server, clients):
    """Create config files for each of the clients."""
    env = Environment(loader=FileSystemLoader('.'))
    for name, settings in clients.items():
        client_template = env.get_template('client.tmpl')
        with open(f"data/client-{name}.conf", "w") as f:
            contents = client_template.render(server=server, client=settings)
            f.write(contents)
        print(f"Created config for client {name}")
        results = subprocess.run(['qr', f'--output=data/{name}.png'], input=contents.encode('utf-8'))
        print(f"Created QR for {name}: {results.returncode}")


def build_files():
    """Create secret config for server, and client config files."""
    server = get_server_info()
    clients = get_clients_info(server['clients'])
    make_secrets(server, clients)
    make_configs(server, clients)
    print("DONE!\n\n")


if __name__ == "__main__":
    build_files()
