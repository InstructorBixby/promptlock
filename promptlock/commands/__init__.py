"""One module per subcommand.

cli.py had become a 400-line file where argument parsing and behaviour
were interleaved, and the next two subcommands were going to make that
worse rather than better.
"""
