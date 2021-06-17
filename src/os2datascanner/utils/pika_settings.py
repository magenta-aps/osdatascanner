from os2datascanner.utils.settings import get_config

_config = get_config('amqp')
AMQP_HOST = _config['AMQP_HOST']
AMQP_USER = _config['AMQP_USER']
AMQP_PWD = _config['AMQP_PWD']
AMQP_SCHEME = _config['AMQP_SCHEME']
AMQP_PORT = _config['AMQP_PORT']
AMQP_VHOST = _config['AMQP_VHOST']
AMQP_BACKOFF_PARAMS = _config.get('AMQP_BACKOFF_PARAMS', {})

del get_config
