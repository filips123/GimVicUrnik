# GimVičUrnik Frontend

This is the frontend part of the GimVičUrnik system.

## Installation

GimVičUrnik requires [Node.js](https://nodejs.org/) version 18.0 or higher and [Yarn](https://yarnpkg.com/) dependency manager.

Firstly clone this repository if you haven't already:
```sh
git clone https://github.com/filips123/GimVicUrnik.git
```

Go to the website folder:
```sh
cd GimVicUrnik/website
```

Install the dependencies:
```sh
yarn
```

## Configuration

GimVičUrnik website uses `.env` file for configuration. Example file can be found at [`.env.sample`](.env.sample).
Mind that you will need to change your WEBSITE an API path.

## Compile and Hot-Reload for Development

```sh
yarn dev
```

## Type-Check, Compile and Minify for Production

```sh
yarn build
```

## Format with [Prettier](https://prettier.io/)

```sh
yarn format
```

## Lint with [ESLint](https://eslint.org/)

```sh
yarn lint
```

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur) + [TypeScript Vue Plugin (Volar)](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin). And don't forget to configure [Volar Takeover Mode](https://vuejs.org/guide/typescript/overview.html#volar-takeover-mode)