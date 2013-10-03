AFSK – Bell 202 Audio Frequency Shift Keying encoder
====================================================

Generates Bell 202 AFSK audio samples and AFSK encoded 
APRS/AX.25 packets.

Installation
------------

Change to the afsk directory and install with::

    $ pip install -r requirements.txt
    $ pip install .

Requires Python 2.6 or 2.7.

If you don't need soundcard playback, the PyAudio dependency is 
optional. Comment it out of the requirements.txt file before
installing. 

You can still use the CLI program with the ``-o`` option to output
to a Wave file. 

Command Line Interface
----------------------

Generate APRS messages with the ``aprs`` CLI program::

    $ aprs --callsign <your callsign> ":EMAIL    :test@example.com Test email"

Specify your message body with INFO command line argument. Be sure to wrap the message in 
quotes so it's passed as one argument, spaces includd. 

At the moment, no message formats are implemented in the ``aprs`` program; you must 
construct the body string yourself. For instance, in the example above, the string 
passed as an argument to ``aprs`` follows the email messsage format specified for APRS. 

You *must* specify your amateur radio callsign with the ``--callsign`` or ``-c`` flags.

Use the ``--output`` option to write audio to a Wave file (use '-' for STDOUT) rather 
than play over the soundcard. 

Get a listing of other options with ``aprs --help``.

