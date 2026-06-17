import { QuartzComponent } from '@quartz-community/types';

interface D3Config {
    drag: boolean;
    zoom: boolean;
    depth: number;
    scale: number;
    repelForce: number;
    centerForce: number;
    linkDistance: number;
    fontSize: number;
    opacityScale: number;
    removeTags: string[];
    showTags: boolean;
    focusOnHover?: boolean;
    enableRadial?: boolean;
    /** Hide nodes whose slug starts with any of these prefixes, e.g. ["tags/"]. */
    excludePrefixes?: string[];
    /** Scale factor applied to every node's radius. */
    nodeSizeMultiplier?: number;
    /** Draw a directional arrowhead at the target end of each link. */
    showArrow?: boolean;
    /** Colour nodes by their top-level folder, e.g. { "organisations": "#e07a5f" }. */
    colorGroups?: Record<string, string>;
    /** Pull same-group nodes toward a shared anchor (0 = off). Creates group clusters. */
    groupForce?: number;
    /** Remove nodes with no edges (keeps the current page). */
    removeOrphans?: boolean;
}
interface GraphOptions {
    localGraph?: Partial<D3Config>;
    globalGraph?: Partial<D3Config>;
}
declare const _default: (userOpts?: Partial<GraphOptions>) => QuartzComponent;

export { type D3Config, _default as Graph, type GraphOptions };
