import os
import sys
import subprocess


def generate_keys():
    result = subprocess.run(['wg', 'genkey'], stdout=subprocess.PIPE)
    pvt = result.stdout.decode('utf-8').rstrip()
    result = subprocess.run(['wg', 'pubkey'], stdout=subprocess.PIPE, input=result.stdout)
    pub = result.stdout.decode('utf-8').rstrip()
    return (pvt, pub)


def generate(name, index):
    """Create files with public and private keys and IP index."""
    if name == "server" or index == "1":
        print("Creating server keys(1)")
        name = "server"
        index = "1"
    else:
        print(f"Creating keys for {name}({index})")
    if not os.path.exists('data'):
        os.mkdir('data')
    elif os.path.exists(f"data/{name}.ini"):
        print(f"ERROR! Already have a config file for name '{name}'\n\n")
        sys.exit(1)
    pvt_key, pub_key = generate_keys()
    with open(f"data/{name}.ini", "w") as f:
        f.write("[DEFAULT]\n")
        f.write(f"pvt_key = {pvt_key}\n")
        f.write(f"pub_key = {pub_key}\n")
        f.write(f"index = {index}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("ERROR! You must provide name and IP index (1+).\n\n")
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2])
