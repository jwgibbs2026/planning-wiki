// One-shot script to regenerate .quartz/plugins/index.ts without importing quartz config
import { regeneratePluginIndex } from "./quartz/plugins/loader/gitLoader.js"
await regeneratePluginIndex({ verbose: true })
console.log("Done.")
