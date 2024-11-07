import protocols.gopher as gopher
from cli import init_db

init_db()

def alt(request):
    if request.path == '/':
        return [gopher.Item(text='root')]
    if request.path == '/test':
        return [gopher.Item(text='test!')]

gopher.serve(
    host="127.0.0.1",
    port=443,
    tls=True,  # Ensure TLS is enabled
    tls_cert_chain='tls/cacert.pem',  # Path to your certificate
    tls_private_key='tls/privkey.pem',  # Path to your private key
    alt_handler=alt
)