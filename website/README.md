GimVičUrnik - Website
=====================

A website for a school timetable, substitutions and menus at Gimnazija Vič.

## Description

This is the website part of the GimVičUrnik system. For more details see [the main README file](../README.md).

## Installation

GimVičUrnik website requires Node.js 20 or later, and [Yarn](https://yarnpkg.com/) dependency manager, installed using [`corepack`](https://nodejs.org/docs/latest-v20.x/api/corepack.html):

```bash
corepack enable
```

You can then clone this repository and install dependencies:

```bash
git clone https://github.com/filips123/GimVicUrnik.git
cd GimVicUrnik/website
yarn install
```

## Usage

### Configuration

GimVičUrnik website uses `.env` file for configuration. Example file can be found at [`.env.sample`](.env.sample).

The official API server only allows requests from the official website, so you will also have to set up your own API server.

Make sure that you do not delete any environment variables. If you want to unset specific variables, set them to an empty string instead.

### Development Server

Development server can be started using:

```bash
yarn dev
```

This will automatically build the website and start the development server with hot reloading.

### Building for Production

Website can be built for production using:

```bash
yarn build
```

This will build the website and save it into the `dist` directory.

### Hosting for Production

The website uses Vue Router in `history` mode, so a simple static file server will fail. You will need to configure your web server to fall back to `index.html` for any non-file requests.

See [Vue Documentation](https://vuejs.org/guide/best-practices/production-deployment#with-build-tools) for more details.

## Contributing

The website uses ESLint for linting and Prettier for formatting the code. They are included in the project's development dependencies.

Please make sure that your changes are formatted correctly according to the code style:

* Linting: `yarn lint --fix`
* Formatting: `yarn format --write`
* Typechecking: `yarn typecheck`
