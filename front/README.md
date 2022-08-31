# laSwarmWiki

## Installation

### Manual

1. Install [Node.js](https://nodejs.org).

1. Install [redis-server](https://redis.io).

   ```console
   # Linux, for example with Debian based systems
   apt install redis-server

   # macOS
   brew install redis
   ```

1. Clone and set up the repository.

   ```console
   git clone https://github.com/laboon-org/laSwarmWiki
   cd laSwarmWiki
   npm install --no-optional
   cp config.js.template config.js # edit the file to suit your environment
   redis-server
   npm start
   ```

laSwarmWiki should now be running at <http://localhost:8080>.

### Docker & docker compose

You can build a production image by running `docker build .` in the repo's root.

For development, there's a `docker-compose.yml` that mounts the app code (for hot reload of code changes) and default config. Before running it, you need to install the dependencies:

```
$ docker-compose run --rm web npm install --no-optionals
$ docker-compose up
```
