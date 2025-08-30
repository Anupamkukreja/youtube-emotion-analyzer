# Gunicorn configuration file

# The address and port to bind to. Render expects 0.0.0.0 and port 10000.
bind = "0.0.0.0:10000"

# Use the efficient 'gevent' worker class for handling long requests.
worker_class = "gevent"

# The number of worker processes. Render's free tier has limited resources, so 1 is best.
workers = 1

# The maximum time a worker can spend handling a request before being restarted.
# 120 seconds should be more than enough for the AI model to process comments.
timeout = 120
