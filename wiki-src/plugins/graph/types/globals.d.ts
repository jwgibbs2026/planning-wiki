// Ambient declarations for non-TS imports bundled by esbuild/tsup.
// graph.scss and *.inline.ts are imported as strings (text loader).
declare module "*.scss" {
  const content: string
  export default content
}

declare module "*.inline.ts" {
  const content: string
  export default content
}
