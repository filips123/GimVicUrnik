GimVičUrnik
===========

A website for a school timetable, substitutions and menus at Gimnazija Vič.

## Description

This is the website part of the GimVičUrnik system. For more details see [the main README file](../README.md).

## Installation

GimVičUrnik website requires Node.js or later and [Yarn](https://yarnpkg.com/) dependency manager.

You can then clone this repository and install dependencies:

```bash
git clone https://github.com/filips123/GimVicUrnik.git
cd GimVicUrnik/website
yarn
```

## Usage

### Configuration

GimVičUrnik website uses `.env` file for configuration. Example file can be found at [`.env.sample`](.env.sample). The official API server only allows requests from the official website, so you will also have to set up your own API server. If you don't plan to use Sentry, you can delete its section entirely.

You can also set configuration using your environment variables or in one of `.env` files [supported by Vue CLI](https://cli.vuejs.org/guide/mode-and-env.html).

### Development server

Development server can be started using:

```bash
yarn serve
```

This will automatically build the website and start the server. It includes automatic hot reloading, code linting and support for single page apps.

### Building for production

Website can be built for production using:

```bash
yarn build
```

It will build whole website, optimized for production and save it into `dist` directory. This will also include all assets and service worker file.

### Hosting for production

The website uses Vue Router in `history` mode, so a simple static file server will fail. You will need to configure your web server to fallback to `index.html` for any non-file requests.

See [Vue Documentation](https://cli.vuejs.org/guide/deployment.html) for more details.

## Contributing

The website uses ESLint with JavaScript Standard Style with TypeScript and Vue extensions. They are included in project's development dependencies.

Please make sure that your changes are formatted correctly according to the code style:

* Linting: `yarn lint --no-fix`
* Formatting: `yarn lint`
