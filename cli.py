import importlib
import sys
import os
import json
import copy
import protocols.gopher as gopher
from protocols.gopher import Item, parse_url, parse_menu, errors
import sqlite3

settings = {
    # Pituophis server options
    'host': 'your.live.host',
    'port': 70,
    'pub_dir': 'pub/',

    # Gophew
    'index': 'db.json',  # Index to use (generated by crawler.py)
    'alternate_titles': True,  # Whether to display alternate titles
    'referrers': True,  # Whether to display referring URLs
    'search_path': '/search', # What the path must start with in order to do a search (a file shouldn't exist here for the alt handler to go off)
    'typestrings': True, # Allow filtering searches by type, i.e. /search01 for textfiles and directories.
    'root_path': '/',  # Path to link to on the results page
    'allow_empty_queries': False,  # Whether to allow empty search queries

    # Comments
    'comments_path': '/comment',  # Path to view comments
    'comments_add_path': '/add-comment',  # Path to add a comment
    
    # Below lines can be disabled by setting them to None
    'root_text': 'Back to root',
    'new_search_text': 'Try another search', 
    'new_search_text_same_filter': 'Try another search with the same criteria',
    'results_caption': 'Results for {} (out of {} items)',
    'types_caption': 'Filtering types: {}',
    'empty_queries_not_allowed_msg': 'Empty search queries are not allowed on this server.'
}

if os.path.isfile(settings['index']):
    with open(settings['index'], 'r') as fp:
        db = json.load(fp)

def init_db():
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('comments.db')
    cursor = conn.cursor()

    # Create a comments table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comment TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Call this function once at the start of your application
init_db()

def add_comment(text):
    conn = sqlite3.connect('comments.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO comments (comment) VALUES (?)', (text,))
    conn.commit()
    conn.close()

def get_comments():
    conn = sqlite3.connect('comments.db')
    cursor = conn.cursor()
    cursor.execute('SELECT comment FROM comments')
    comments = [row[0] for row in cursor.fetchall()]
    conn.close()
    return comments

def format_comments_as_table(comments):
    # Define headers
    headers = ["ID", "Comment"]

    # Determine the width of each column, accounting for the ID column and comment length
    col_widths = [
        max(len(str(index + 1)) for index in range(len(comments))) if comments else len(headers[0]),
        max(len(comment) for comment in comments) if comments else len(headers[1])
    ]
    col_widths = [max(col_widths[i], len(headers[i])) for i in range(len(headers))]

    # Create header and separator rows
    temp = f"| {' | '.join(headers[i].ljust(col_widths[i]) for i in range(len(headers)))} |"
    header_row = "\033[38;2;255;255;0m\033[48;2;128;0;128m" + temp + "\033[0m"
    # header_row = f"| {' | '.join(headers[i].ljust(col_widths[i]) for i in range(len(headers)))} |"
    temp2 = f"+{'-+-'.join('-' * (col_widths[i] + 1) for i in range(len(headers)))}+"
    separator_row = "\033[38;2;255;255;0m\033[48;2;128;0;128m" + temp2 + "\033[0m"
    # separator_row = f"+{'-+-'.join('-' * (col_widths[i] + 1) for i in range(len(headers)))}+"

    # Format each row of comments with an auto-incrementing ID
    formatted_comments = [
        f"| {str(index + 1).ljust(col_widths[0])} | {comment.ljust(col_widths[1])} |"
        for index, comment in enumerate(comments)
    ]

    # Return the table as a list of lines
    return [separator_row, header_row, separator_row] + formatted_comments + [separator_row]


def alt(request):
    if request.path.startswith(settings['search_path']):
        typestring = request.path.replace(settings['search_path'], '').replace('/', '')
        types = list(typestring)
        menu = []
        if not settings['root_text'] is None:
            menu.append(Item(itype='1', text=settings['root_text'], path='/', host=request.host, port=request.port))
        if not settings['new_search_text'] is None:
            menu.append(Item(itype='7', text=settings['new_search_text'], path=settings['search_path'], host=request.host, port=request.port))
        if (not request.path == settings['search_path']) and not settings['new_search_text_same_filter'] is None:
            menu.append(Item(itype='7', text=settings['new_search_text_same_filter'], path=request.path, host=request.host, port=request.port))
        if not settings['results_caption'] is None:
            menu.append(Item(text=settings['results_caption'].format(request.query, len(db['items']))))
        if not settings['types_caption'] is None:
            if len(types):
                menu.append(Item(text=settings['types_caption'].format(', '.join(types))))
        if (not settings['allow_empty_queries']) and request.query == '':
            return Item(text=settings['empty_queries_not_allowed_msg'], itype='3')
        items = db['items']
        for item in items:
            sampling = item
            for title in db['items'][item]['titles']:
                sampling += title
            if request.query.lower() in sampling.lower():
                req = parse_url(item)
                yes = False
                if len(types) == 0:
                    yes = True
                else:
                    if req.type in types:
                        yes = True
                if yes:
                    try:
                        menu.append(Item(text=''))
                        menu.append(Item(itype=req.type, text=items[item]['titles'][0], path=req.path, host=req.host, port=req.port))
                        menu.append(Item(text='URL: ' + req.url()))
                        if len(items[items]['titles']) > 1:
                            if settings['alternate_titles']:
                                menu.append(item(text='Alternate titles:'))
                                for title in items[item]['titles'][1:]:
                                    menu.append(item(text='  ' + title))
                            if settings['referrers']:
                                menu.append(Item(text='Referred by:'))
                                for referrer in items[item]['referrers']:
                                    menu.append(Item(text='  ' + referrer))
                    except:
                        pass
        return menu
    
    elif request.path.startswith(settings['comments_add_path']):
        # Append the new comment (from `query`) to the comments list
        if request.query:
            add_comment(request.query)
            print('Comment added:', request.query)
            menu = [Item(text="Comment added! Thank you."),
                    Item(itype='1', text="View comments", path=settings['comments_path'], host=request.host, port=request.port)]
            return menu
        else:
            # If no comment text was entered, prompt the user again
            menu = [Item(text="No comment provided! Please try again."),
                    Item(itype='7', text="Add a comment.", path=settings['comments_add_path'], host=request.host, port=request.port)]
            return menu
        
    elif request.path.startswith(settings['comments_path']):
        # Default path to view comments
        menu = [Item(text="\033[31m-------------------------------\033[0m"),
                Item(text='Welcome to the Comment Section!'),
                Item(text="-------------------------------"),
                Item(itype='1', text=settings['root_text'], path='/', host=request.host, port=request.port),
                Item(),  # Blank line
                Item(itype='7', text="Add a comment.", path=settings['comments_add_path'], host=request.host, port=request.port),
                Item(),  # Blank line
                Item(text="Comments:"),  # Section header
                ]
        comments = get_comments()
        if not comments:
            menu.append(gopher.Item(text="There are no messages yet... be the first!"))
        else:
            # Format comments as a table and add each line as a separate item
            table_lines = format_comments_as_table(comments)
            for line in table_lines:
                entry = "\033[1;32;40m" + line + "\033[0m"
                menu.append(gopher.Item(text=entry))
            menu.append(Item())
        return menu
    
        # # Append the new comment (from `query`) to the comments list
        # if request.query:
        #     add_comment(request.query)
        #     menu = [Item(text="Comment added! Thank you."),
        #             Item(itype='1', text="View comments", path="/", host=request.host, port=request.port)]
        # else:
        #     # If no comment text was entered, prompt the user again
        #     menu = [Item(text="No comment provided! Please try again."),
        #             Item(itype='7', text="Add a comment.", path=settings['comments_path'], host=request.host, port=request.port)]
        #     return menu
    else:
        e = copy.copy(errors['404'])
        e.text = e.text.format(request.path)
        return e

# check if the user is running the script with the correct number of arguments
if len(sys.argv) < 2:
    # if not, print the usage
    print('usage: gopher [command] cd [options]')
    print('Commands:')
    print('  serve [options]')
    print('  fetch [url] [options]')
    print('Server Options:')
    print('  -H, --host=HOST\t\tAdvertised host (default: 127.0.0.1)')
    print('  -p, --port=PORT\t\tPort to bind to (default: 70)')
    print('  -a, --advertised-port=PORT\tPort to advertise')
    print('  -d, --directory=DIR\t\tDirectory to serve (default: pub/)')
    print('  -A, --alt-handler=HANDLER\tAlternate handler to use if 404 error is generated (python file with it defined as "def alt(request):")')
    print('  -s, --send-period\t\tSend a period at the end of each response (default: False)')
    print('  -D, --debug\t\t\tPrint requests as they are received (default: False)')
    print('  -v, --version\t\t\tPrint version')
    print('Fetch Options:')
    print('  -o, --output=FILE\t\tFile to write to (default: stdout)')
else:
    # check if the user is serving or fetching
    if sys.argv[1] == 'serve':
        # check for arguments
        # host
        host = '127.0.0.1'
        if '-H' in sys.argv or '--host' in sys.argv:
            host = sys.argv[sys.argv.index('-H') + 1]
        # port
        port = 70
        if '-p' in sys.argv or '--port' in sys.argv:
            port = int(sys.argv[sys.argv.index('-p') + 1])
        # advertised port
        advertised_port = None
        if '-a' in sys.argv or '--advertised-port' in sys.argv:
            advertised_port = int(sys.argv[sys.argv.index('-a') + 1])
        # directory
        pub_dir = 'pub/'
        if '-d' in sys.argv or '--directory' in sys.argv:
            pub_dir = sys.argv[sys.argv.index('-d') + 1]
        # alternate handler
        alt_handler = True
        if '-A' in sys.argv or '--alt-handler' in sys.argv:
            print('loading alt handler')
            alt_handler = alt
        # tls
        tls = False
        tls_cert_chain = None
        tls_private_key = None
        if '-tls' in sys.argv:
            tls=True  # Ensure TLS is enabled
            tls_cert_chain='tls/cacert.pem'  # Path to your certificate
            tls_private_key='tls/privkey.pem'  # Path to your private key

        # http
        http = False
        http_port = 8080
        if '-http' in sys.argv:
            http=True
            if '--http-port' in sys.argv:
                http_port = int(sys.argv[sys.argv.index('--http-port') + 1])
        
        # send period
        send_period = False
        if '-s' in sys.argv or '--send-period' in sys.argv:
            send_period = True
        # debug
        debug = False
        if '-D' in sys.argv or '--debug' in sys.argv:
            debug = True
        # start the server
        gopher.serve(host=host, port=port, advertised_port=advertised_port, 
                    tls=tls, tls_cert_chain=tls_cert_chain, tls_private_key=tls_private_key,
                    handler=gopher.handle, pub_dir=pub_dir, alt_handler=alt_handler,
                    run_http=http, http_port=http_port,
                    send_period=send_period, debug=debug)
    elif sys.argv[1] == 'fetch':
        # check for arguments
        # url
        url = sys.argv[2]
        # output file
        output = 'stdout'
        if '-o' in sys.argv or '--output' in sys.argv:
            output = sys.argv[sys.argv.index('-o') + 1]
        # start the fetch
        o = gopher.get(url)
        if output == 'stdout':
            sys.stdout.buffer.write(o.binary)
        else:
            with open(output, 'wb') as f:
                f.write(o.binary)
                f.close()