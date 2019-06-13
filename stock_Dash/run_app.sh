#!/bin/bash

#!/bin/bash

# turn on bash's job control
set -m

# Start the primary process and put it in the background
python3 twitter.py &

# Start the helper process
gunicorn --bind 0.0.0.0:8070 app:app.server

# the my_helper_process might need to know how to wait on the
# primary process to start before it does its work and returns


# now we bring the primary process back into the foreground
# and leave it there
# fg %1