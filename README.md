# Gopherism


## Installation
```
pip3 install -r requirements.txt
```

## Guide
Start the Gopher server using:
```
python cli.py serve -H 127.0.0.1 -p 443 -d pub/ -tls -A
```
- `-H`: advertised host (default: 127.0.0.1)
- `-p`: port to use for Gopher (default: 70)
- `-d`: directory to serve gopher items from (default: 'pub/')
- `-tls`: indicates to enable TLS encryption (default: False)
- `-http`: indicates to create a HTTP server that runs in separate thread (default: False)
- `-http_port`: port to use for HTTP (default: 8080)
- `-A`: special handler to include database search and comment section

To spin up a Gopher client, I am using [VF-1](https://git.sr.ht/~solderpunk/VF-1). After running the above CLI command, in a separate terminal, do:
```
python vf1.py
```
You should see the VF-1 command line Gopher client appear. To enable TLS encryption, type `tls`. To go to your hosted gopher site, enter `go gopher://localhost:<PORT>`. See the images below for an example interaction.

**Localhost**

![VF-1 Localhost interaction](./assets/vf1_localhost_demo.png)

**Public Gopher Site**


![VF-1 Public interaction](./assets/vf1_public_demo.png)


## Packet Capturing with Wireshark

**TCP packets**
Gopher operates over TCP. You can filter for these packets in Wireshark using `tcp.port == <PORT>>` after spinning up the Gopher server and connecting to it:
![TLS Wireshark Packets](./assets/tcp_packets.png)


**TLS**
To capture TLS packets, you need to deploy your Gopher server with TLS encryption, as explained in the guide earlier. Note that for demonstration purposes, a **self-signed certificate** and private key for TLS has been generated via
```
openssl req -x509 -newkey rsa:4096 -keyout privkey.pem -out cacert.pem -days 365 -nodes
```
and stored in the `/tls` folder. Because the certificate is self-signed, this can pose an issue for loading the site. As such, I disabled SSL certificate verification in lines 455-458 of `vf1.py`:
```
if self.tls:
    context = ssl.create_default_context()
    context.check_hostname = False  # Disable hostname checking
    context.verify_mode = ssl.CERT_NONE  # Disable certificate verification
    s = context.wrap_socket(s, server_hostname = gi.host)
```
This allows us to bypass the certificate verfication error. For analyzing packets over Wireshark, default port should be 443. To verify, go `Wireshark > Preferences > Protocols > HTTP` to see the default port number for "SSL/TLS Ports" in settings. It is important to match the port else the TLS packets won't be labelled properly. You should start seeing TLS-encrypted packets appear in Wireshark when you filter for `tls`:
![TLS Wireshark Packets](./assets/tls_packets.png)


## References
The implementations for the Gopher server is referenced from `Pituophis` amd the terminal from `VF-1`:
[VF-1 Code](https://git.sr.ht/~solderpunk/VF-1)
[VF-1 Docs](https://manpages.ubuntu.com/manpages/jammy/man1/vf1.1.html)
[Pituophis Github](https://github.com/dotcomboom/Pituophis/tree/master)
[Pituophis Old Docs (with TLS)](https://pituophis.readthedocs.io/_/downloads/en/v1.1/pdf/)

