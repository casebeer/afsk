AFSK and ``aprs``
=================

Library to generate Bell 202 AFSK audio samples and 
AFSK encoded APRS/AX.25 packets. 

The ``aprs`` command line program encodes APRS packets 
as AFSK audio data. 

e.g.::

    $ aprs -c <your callsign> ":EMAIL    :test@example.com Test email"

Installation
------------

Install with ``pip``::

    $ pip install afsk
    $ pip install --allow-external PyAudio --allow-unverified PyAudio PyAudio

PyAudio is optional, so must be installed separately. 

If you want to use the CLI program to play APRS packets via your
soundcard, install PyAudio. Otherwise, if you just want to generate
Wave files of AFSK data, you can skip it. 

Note that installing PyAudio will require a C compiler and PyAudio's various
C dependencies, in addition to the ``--allow-external`` and ``--allow-unverified``
``pip`` flags. 

For development, change to the afsk directory and install with::

    $ pip install -r requirements.txt
    $ python setup.py develop

Requires Python 2.6 or 2.7.

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

Examples
--------

Playback with PyAudio and short options::

    $ aprs --callsign <your callsign> ":EMAIL    :test@example.com Test email"

Playback with ``sox``::

    $ aprs --callsign <your callsign> --output - ":EMAIL    :test@example.com Test email" |\
          play -t wav -

Save to a wave file with using short options::

    $ aprs -c <your callsign> -o packet.wav ":EMAIL    :test@example.com Test email"

Contributing
------------

Get the source and report any bugs on Github:

    https://github.com/casebeer/afsk

Version History
---------------

- 0.0.3 – Pin dependency versions, fix bug with STDOUT playback, verbosity CLI option. 

