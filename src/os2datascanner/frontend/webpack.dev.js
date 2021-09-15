const configs = require('./webpack.base')

configs.map(config => {
  config.mode = 'development'
  config.watch = true
  config.watchOptions = {
    aggregateTimeout: 300,
    ignored: ['node_modules']
  }
})

module.exports = configs
