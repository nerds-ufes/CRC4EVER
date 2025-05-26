About the CRC4EVER

The CRC4EVER architecture is specifically designed for path verification and routing using a unique encoding scheme. It operates within programmable P4 switches, leveraging CRC-based operations at its core

# P7 + PolKa + PoT

**This is still a work in progress. Feedback is welcome!**

## Requirements

- git
- python3
- matplotlib
- networkX
- regex
- polka-routing

## Download

```
git clone https://github.com/nerds-ufes/CRC4EVER.git
cd CRC4EVER
```

## Run P7 + Polka + PoT

### Prepare the Environment

It is recommended to have five open terminals.

1. Compile P4 code and run Tofino.
2. Load table information and configure ports.
3. Create the topology and generate files.
4. Host 1.
5. Host 2.

### Create the Topology and Generate Files

In **Terminal 3**, edit the *main.py* file with the topology, ports, PoT, and links information.

```
cd CRC4EVER
nano main.py
```

Generate the necessary files.
```
python main.py
```

Place the files in the correct directories.
```
./set_files.sh
```

### Compile P4 Code and Run Tofino Switch

In **Terminal 1**, compile the P4 code using the official P4 compiler.

If you are using P4 Studio, follow the next steps to compile the P4 codes:

```
cd bf-sde-9.13.2
```
```
. ../tools/set_sde.bash
```
Compile the custom P4 code (Verification pipeline):
```
../tools/p4_build.sh ~/CRC4EVER/p4src/p7calc_mod.p4
```
Compile P7 and (Forward pipeline) p4 code:

```
../tools/p4_build.sh ~/CRC4EVER/p4src/p7_polka.p4
```

Run the switch:

```
./run_switchd.sh -p p7_polka p7calc_mod -c ~/CRC4EVER/p4src/multiprogram_custom_bfrt.conf
```

### Load the Tables and Set Ports

In **Terminal 2**:
```
cd bf-sde-9.13.2
```
```
. ../tools/set_sde.bash
```
Load table information:
```
bfshell -b ~CRC4EVER/files/bfrt.py
```
Configure ports:
```
bfshell -f ~/CRC4EVER/files/ports_config.txt -i
```

### Send Traffic

In **Terminal 4**, access host 1.

Configure the VLAN for P7 (change the interface name and the IP for your setup):

```
sudo ip link add link enp3s0f0 name enp3s0f0.1920 type vlan id 1920
```
```
sudo ifconfig enp3s0f0.1920 10.0.0.10 up
```

In **Terminal 5**, access host 2.

Configure the VLAN for P7 (change the interface name and the IP for your setup):
```
sudo ip link add link enp6s0f0 name enp6s0f0.1920 type vlan id 1920
```
```
sudo ifconfig enp6s0f0.1920 10.0.0.20 up

```

To troubleshoot the route that PolKa is using to reach the destination, you can use the TTL field.

The file [calculator](https://docs.google.com/spreadsheets/d/19dWWfbyr4qZv1m4FIzHOO8c77znra906RL7u58ySk80/edit?usp=sharing) shows the information of the tables and the result of the TTL when it reaches the destination.

For example, a ping from H1 to H2:

```
ping 10.0.0.20 -Q 23
```

The response should have a TTL of 103* (64 + 40).

\*The initial TTL is 64.

### Slice

Each slice can be selected at the host by choosing a different **ToS (Type of Service)** value, or by using different **TCP/UDP ports**.

![Path Selection](image.png) <!-- Substitua pelo nome correto da imagem -->

Select the slice that corresponds to the desired path, as illustrated in the figure:
- **Path 1** — Blue
- **Path 2** — Red
- **Path 3** — Yellow

To use a specific PolKA routeID, use ping. Then, you can specify the ToS

If you are using **ToS** as the selection parameter:
- Use **21** for **Path 1 (Blue)**
```
ping -Q 21 10.0.0.20

- Use **22** for **Path 2 (Red)**
```
ping -Q 22 10.0.0.20

- Use **23** for **Path 3 (Yellow)**
```
ping -Q 23 10.0.0.20


#### PoT — Proof of Transit (Path Verification)

The **Proof of Transit (PoT)** mechanism relies on a unique mapping between the `routeID` and the sequence of node identifiers (`nodeIDs`) and port identifiers (`portIDs`) along the path to generate a **path signature**.

### PoT Calculation Formula

PoTᵢ = CRC32( nodeIDᵢ || portIDᵢ || PoTᵢ₋₁ )

Where:
- `nodeIDᵢ` = Identifier of node *i*
- `portIDᵢ` = Egress port of node *i*
- `PoTᵢ₋₁` = PoT value from the previous hop

This mechanism enables intrinsic path verification by performing **end-to-end PoT** through chained CRC32 computations. Each node along the path updates the PoT value based on its own `nodeID` and `portID`, combined with the previous PoT value. At the egress node, the verification process checks the final PoT metadata to confirm that the packet has traversed the expected path.

---

### Debugging Path Verification

1. Open the P4 source file:

```
nano ~/CRC4EVER/p4src/p7_polka.p4

2. Enable the function:
send_to_debug()

With this function enabled, the PoT value is sent back to the **source MAC address**, allowing PoT inspection for debugging purposes. After enabling it, **recompile the forwarding pipeline**.

---

### Testing with Scapy (Packet Sender)

At **Host 1 (source)**, use the Scapy script `send3.py` to send a packet with the desired ToS (which selects the path):

```bash
python3 send3.py

Replace 21 with:
21 for Path 1
22 for Path 2
23 for Path 3

Capturing and Verifying PoT

At **Host 2 (destination)**, use the provided tcpdump script hash_collect.sh to capture packets and display the PoT metadata:

```
bash hash_collect.sh

This script extracts and displays the PoT value for validation and verification.


[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


## Team
We are members of [**NERDS** — *Nucleus for Studies in Software Defined Networks*](https://nerds-ufes.github.io/polka/index.html) at the **Federal University of Espírito Santo (UFES)** in Vitória, Espírito Santo, Brazil; [**INTRIG** — *Information & Networking Technologies Research & Innovation Group*](http://intrig.dca.fee.unicamp.br) at the **University of Campinas (Unicamp)**.

## Contributing
PRs are very much appreciated. For bugs/features consider creating an issue before sending a PR.

## Documentation
For further information about P7, please read our wiki (https://github.com/intrig-unicamp/p7/wiki)
For further information about PoLKA please read our website (https://nerds-ufes.github.io/polka/index.html)

Thanks to all contributors

