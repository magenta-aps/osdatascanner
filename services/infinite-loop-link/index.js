const http = require('http')

const host = 'localhost'
const port = 3000

const requestListener = function (req, res) {
  res.setHeader('Content-Type', 'text/html')
  res.writeHead(200)
  res.end(`<!doctype html><html lang="da"><head><meta charset="utf-8"><title>dummy</title></head><body><a href="?q=${Date.now()}">this is a link</a></body></html>`)
}

const server = http.createServer(requestListener)
server.listen(port, host, () => {
    console.log(`Server is running on http://${host}:${port}`)
})
