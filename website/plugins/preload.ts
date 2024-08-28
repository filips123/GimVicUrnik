import { readFileSync, writeFileSync } from 'fs'
import { resolve } from 'path'
import { type Plugin } from 'vite'

const defaultManifestFilename = '.vite/manifest.json'
const defaultPreloadFilename = '.vite/preload.conf'

interface PreloadEntry {
  resource: string
  rel: string
  as?: string
  crossorigin?: boolean | string
}

interface PreloadEntries {
  [view: string]: PreloadEntry[]
}

function generateApacheConfig(entries: PreloadEntries): string {
  let config = ''

  for (const [view, resources] of Object.entries(entries)) {
    config += `<LocationMatch "${view}">\n`

    const deduplicated = [...new Map(resources.map(item => [item.resource, item])).values()]

    for (const { resource, rel, as, crossorigin } of deduplicated) {
      let header = `\tHeader append Link "<${resource}>; rel=${rel}`
      if (as) header += `; as=${as}`
      if (crossorigin === true) header += '; crossorigin'
      else if (crossorigin) header += `; crossorigin=${crossorigin}`
      header += '"\n'
      config += header
    }

    config += `</LocationMatch>\n\n`
  }

  return config
}

function collectResources(
  chunkName: string,
  manifest: Record<string, any>,
  collected: PreloadEntry[],
) {
  const chunk = manifest[chunkName]
  if (!chunk) return

  for (const cssFile of chunk.css || []) {
    const crossorigin = cssFile.startsWith('css/index.')
    collected.push({ resource: `/${cssFile}`, rel: 'preload', as: 'style', crossorigin })
  }

  if (chunk.file) {
    collected.push({ resource: `/${chunk.file}`, rel: 'modulepreload' })
  }

  for (const importedChunk of chunk.imports || []) {
    collectResources(importedChunk, manifest, collected)
  }
}

/**
 * Generates an Apache configuration file for preloading resources.
 */
export default function ApachePreload(views: Record<string, string>): Plugin {
  let manifestPath: string | undefined
  let preloadPath: string | undefined

  return {
    name: 'vite-plugin-apache-preload',
    apply: 'build',
    configResolved(config) {
      if (config.build.manifest) {
        const manifestFilename =
          typeof config.build.manifest === 'string'
            ? config.build.manifest
            : defaultManifestFilename
        manifestPath = resolve(config.root, config.build.outDir, manifestFilename)
        preloadPath = resolve(config.root, config.build.outDir, defaultPreloadFilename)
      }
    },
    writeBundle() {
      if (!manifestPath || !preloadPath) return

      const manifest = JSON.parse(readFileSync(manifestPath, 'utf-8'))
      const collected: PreloadEntries = {}

      for (const [location, view] of Object.entries(views)) {
        collected[location] = []
        collectResources(view, manifest, collected[location])
      }

      const apacheConfig = generateApacheConfig(collected)
      writeFileSync(preloadPath, apacheConfig)
    },
  }
}
