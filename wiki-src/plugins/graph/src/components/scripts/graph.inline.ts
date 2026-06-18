// @ts-nocheck
import {
  removeAllChildren,
  getBasePath,
  getFullSlugFromUrl,
  simplifySlug,
  resolveBasePath,
} from "@quartz-community/utils";

(function () {
  function getSlugFromUrl() {
    var slug = getFullSlugFromUrl();
    var base = getBasePath();
    if (base && slug.startsWith(base.replace(/^\//, ""))) {
      slug = slug.slice(base.replace(/^\//, "").length);
      if (slug.startsWith("/")) slug = slug.slice(1);
    }
    return slug;
  }

  function loadScript(src) {
    var existing = document.querySelector('script[src="' + src + '"]');
    if (existing) return Promise.resolve();
    return new Promise(function (resolve, reject) {
      var script = document.createElement("script");
      script.src = src;
      script.crossOrigin = "anonymous";
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  Promise.all([
    loadScript("https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"),
    loadScript("https://cdn.jsdelivr.net/npm/pixi.js@8/dist/pixi.js"),
  ])
    .then(function () {
      initGraph();
    })
    .catch(function (err) {
      console.error("[Graph] Failed to load libraries:", err);
      var containers = document.querySelectorAll(".graph-container");
      for (var i = 0; i < containers.length; i++) {
        containers[i].textContent = "Graph could not load. Check your network connection.";
        containers[i].style.display = "flex";
        containers[i].style.alignItems = "center";
        containers[i].style.justifyContent = "center";
        containers[i].style.color = "var(--gray)";
        containers[i].style.fontSize = "0.9rem";
      }
    });

  function initGraph() {
    var d3 = window.d3;
    var PIXI = window.PIXI;

    if (!d3 || !PIXI) {
      console.error("[Graph] Libraries not loaded");
      return;
    }

    var localStorageKey = "graph-visited";

    function getVisited() {
      return new Set(JSON.parse(localStorage.getItem(localStorageKey) || "[]"));
    }

    function addToVisited(slug) {
      var visited = getVisited();
      visited.add(slug);
      localStorage.setItem(localStorageKey, JSON.stringify(Array.from(visited)));
    }

    // Resolves CSS color values containing calc()/var() that PixiJS cannot parse.
    // Uses a temp DOM element so the browser's CSS engine evaluates the expression.
    function resolveColor(value, fallback) {
      if (!value) return fallback;
      var el = document.createElement("div");
      el.style.color = value;
      el.style.position = "absolute";
      el.style.visibility = "hidden";
      document.body.appendChild(el);
      var resolved = getComputedStyle(el).color;
      el.remove();
      return resolved || fallback;
    }

    async function renderGraph(graph, fullSlug, renderGeneration) {
      var slug = simplifySlug(fullSlug);
      if (slug === "") slug = "index";
      var visited = getVisited();
      removeAllChildren(graph);

      if (renderGeneration !== undefined && renderGeneration !== currentRenderGeneration) {
        console.log("[Graph] Stale render, skipping");
        return function () {};
      }

      var config = JSON.parse(graph.dataset["cfg"] || "{}");
      var enableDrag = config.drag;
      var enableZoom = config.zoom;
      var depth = config.depth;
      var scale = config.scale || 1;
      var repelForce = config.repelForce || 0.5;
      var centerForce = config.centerForce || 0.3;
      var linkDistance = config.linkDistance || 30;
      var fontSize = config.fontSize || 0.6;
      var opacityScale = config.opacityScale || 1;
      var removeTags = config.removeTags || [];
      var showTags = config.showTags;
      var focusOnHover = config.focusOnHover;
      var enableRadial = config.enableRadial;
      var excludePrefixes = config.excludePrefixes || [];
      var nodeSizeMultiplier = config.nodeSizeMultiplier || 1;
      var showArrow = config.showArrow;
      var colorGroups = config.colorGroups || {};
      var groupForce = config.groupForce || 0;
      var removeOrphans = config.removeOrphans;
      var groupRadius = config.groupRadius || 0.34;
      var groupLabels = config.groupLabels || {};

      function topFolder(id) {
        var i = id.indexOf("/");
        return i >= 0 ? id.slice(0, i) : "";
      }
      function isExcluded(id) {
        for (var p = 0; p < excludePrefixes.length; p++) {
          if (id.indexOf(excludePrefixes[p]) === 0) return true;
        }
        return false;
      }
      // A node's colour/cluster group: its top folder, or — for a top-level hub
      // page whose slug names a group (e.g. "protected-species") — that group.
      // Truly ungrouped pages (wiki home, glossary) return "" and sit centre.
      function groupOf(id) {
        var f = topFolder(id);
        if (f) return f;
        if (colorGroups[id]) return id;
        return "";
      }

      var data;
      try {
        var dataRaw = await fetchData;
        data = new Map();
        for (var key in dataRaw) {
          data.set(simplifySlug(key), dataRaw[key]);
        }
      } catch (err) {
        console.error("[Graph] Error loading data:", err);
        return function () {};
      }

      var width = graph.offsetWidth;
      var height = Math.max(graph.offsetHeight, 250);

      var links = [];
      var allTags = [];
      var validLinks = new Set(data.keys());

      // Drop excluded pages (e.g. tags/*) so they don't appear as orphan nodes.
      if (excludePrefixes.length) {
        validLinks.forEach(function (key) {
          if (isExcluded(key)) validLinks.delete(key);
        });
      }

      data.forEach(function (details, source) {
        if (isExcluded(source)) return;
        var outgoing = details.links || [];
        for (var i = 0; i < outgoing.length; i++) {
          var dest = simplifySlug(outgoing[i]);
          if (validLinks.has(dest)) {
            links.push({ source: source, target: dest });
          }
        }

        if (showTags) {
          var tags = details.tags || [];
          for (var i = 0; i < tags.length; i++) {
            var tag = tags[i];
            if (removeTags.indexOf(tag) === -1) {
              var tagSlug = simplifySlug("tags/" + tag);
              if (allTags.indexOf(tagSlug) === -1) {
                allTags.push(tagSlug);
              }
              links.push({ source: source, target: tagSlug });
            }
          }
        }
      });

      var neighbourhood = new Set();
      if (depth >= 0) {
        var queue = [slug];
        var seen = new Set([slug]);
        for (var d = 0; d <= depth && queue.length > 0; d++) {
          var nextQueue = [];
          for (var qi = 0; qi < queue.length; qi++) {
            var cur = queue[qi];
            neighbourhood.add(cur);
            for (var li = 0; li < links.length; li++) {
              var link = links[li];
              if (link.source === cur && !seen.has(link.target)) {
                seen.add(link.target);
                nextQueue.push(link.target);
              }
              if (link.target === cur && !seen.has(link.source)) {
                seen.add(link.source);
                nextQueue.push(link.source);
              }
            }
          }
          queue = nextQueue;
        }
      } else {
        validLinks.forEach(function (id) {
          neighbourhood.add(id);
        });
        for (var i = 0; i < allTags.length; i++) {
          neighbourhood.add(allTags[i]);
        }
      }

      var nodes = [];
      var nodeMap = new Map();
      neighbourhood.forEach(function (url) {
        var isTag = url.startsWith("tags/");
        var text = isTag ? "#" + url.substring(5) : data.get(url)?.title || url;
        var nodeTags = isTag ? [] : data.get(url)?.tags || [];
        var node = {
          id: url,
          text: text,
          tags: nodeTags,
          group: isTag ? "" : groupOf(url),
          x: Math.random() * width - width / 2,
          y: Math.random() * height - height / 2,
          vx: 0,
          vy: 0,
        };
        nodes.push(node);
        nodeMap.set(url, node);
      });

      var graphLinks = [];
      for (var i = 0; i < links.length; i++) {
        var link = links[i];
        if (neighbourhood.has(link.source) && neighbourhood.has(link.target)) {
          var sourceNode = nodeMap.get(link.source);
          var targetNode = nodeMap.get(link.target);
          if (sourceNode && targetNode) {
            graphLinks.push({ source: sourceNode, target: targetNode });
          }
        }
      }

      // Drop orphan nodes (no edges) so the graph isn't littered with stray
      // dots — e.g. folder index pages. The current page is always kept.
      if (removeOrphans) {
        var degree = {};
        for (var i = 0; i < graphLinks.length; i++) {
          degree[graphLinks[i].source.id] = (degree[graphLinks[i].source.id] || 0) + 1;
          degree[graphLinks[i].target.id] = (degree[graphLinks[i].target.id] || 0) + 1;
        }
        nodes = nodes.filter(function (n) {
          return n.id === slug || degree[n.id] > 0;
        });
        nodeMap = new Map();
        for (var i = 0; i < nodes.length; i++) {
          nodeMap.set(nodes[i].id, nodes[i]);
        }
      }

      var styles = getComputedStyle(document.documentElement);
      var secondary = resolveColor(styles.getPropertyValue("--secondary").trim(), "#c792ea");
      var tertiary = resolveColor(styles.getPropertyValue("--tertiary").trim(), "#82aaff");
      var gray = resolveColor(styles.getPropertyValue("--gray").trim(), "#6c6c6c");
      var lightgray = resolveColor(styles.getPropertyValue("--lightgray").trim(), "#d4d4d4");
      var dark = resolveColor(styles.getPropertyValue("--dark").trim(), "#1a1a1a");
      var light = resolveColor(styles.getPropertyValue("--light").trim(), "#f5f5f5");
      var bodyFont = styles.getPropertyValue("--bodyFont").trim() || "inherit";

      // Resolve per-folder colour groups once (Obsidian-style grouping by top folder).
      var groupColors = {};
      for (var gk in colorGroups) {
        groupColors[gk] = resolveColor(colorGroups[gk], gray);
      }

      var app = new PIXI.Application();
      await app.init({
        width: width,
        height: height,
        antialias: true,
        backgroundAlpha: 0,
        resolution: window.devicePixelRatio || 1,
        autoDensity: true,
        eventMode: "static",
      });

      graph.appendChild(app.canvas);

      // Colour key — only on the full-screen global graph, where there's room.
      if (graph.classList.contains("global-graph-container") && Object.keys(colorGroups).length) {
        var legend = document.createElement("div");
        legend.className = "graph-legend";
        var legendKeys = Object.keys(colorGroups);
        for (var li = 0; li < legendKeys.length; li++) {
          var lk = legendKeys[li];
          var row = document.createElement("div");
          row.className = "graph-legend-item";
          var sw = document.createElement("span");
          sw.className = "graph-legend-swatch";
          sw.style.backgroundColor = groupColors[lk] || gray;
          var lbl = document.createElement("span");
          lbl.textContent = groupLabels[lk] || lk;
          row.appendChild(sw);
          row.appendChild(lbl);
          legend.appendChild(row);
        }
        graph.appendChild(legend);
      }

      var stage = new PIXI.Container();
      app.stage.addChild(stage);

      var simulation = d3
        .forceSimulation(nodes)
        .force("charge", d3.forceManyBody().strength(-100 * repelForce))
        .force("center", d3.forceCenter().strength(centerForce))
        .force("link", d3.forceLink(graphLinks).distance(linkDistance))
        .force(
          "collide",
          d3
            .forceCollide()
            .radius(function (d) {
              var numLinks = 0;
              for (var i = 0; i < graphLinks.length; i++) {
                if (graphLinks[i].source.id === d.id || graphLinks[i].target.id === d.id) {
                  numLinks++;
                }
              }
              return (2 + Math.sqrt(numLinks)) * nodeSizeMultiplier;
            })
            .iterations(3),
        );

      if (enableRadial) {
        var radius = (Math.min(width, height) / 2) * 0.8;
        simulation.force("radial", d3.forceRadial(radius).strength(0.2));
      }

      // Group "orbits": each topic folder (a colorGroups key) gets an anchor
      // arranged around a circle; ungrouped hub pages (e.g. the wiki home and
      // Glossary) are pulled firmly to the centre so everything orbits them.
      if (groupForce > 0) {
        var groupList = Object.keys(colorGroups);
        var anchorRadius = Math.min(width, height) * groupRadius;
        var groupAnchors = {};
        for (var i = 0; i < groupList.length; i++) {
          var angle = (i / groupList.length) * 2 * Math.PI - Math.PI / 2;
          groupAnchors[groupList[i]] = {
            x: Math.cos(angle) * anchorRadius,
            y: Math.sin(angle) * anchorRadius,
          };
        }
        var centreStrength = Math.max(groupForce * 2, 0.6);
        function groupAnchor(d) {
          return groupAnchors[d.group] || { x: 0, y: 0 };
        }
        function groupAnchorStrength(d) {
          return groupAnchors[d.group] ? groupForce : centreStrength;
        }
        simulation.force(
          "groupX",
          d3.forceX(function (d) { return groupAnchor(d).x; }).strength(groupAnchorStrength),
        );
        simulation.force(
          "groupY",
          d3.forceY(function (d) { return groupAnchor(d).y; }).strength(groupAnchorStrength),
        );
      }

      var linkContainer = new PIXI.Container();
      var nodesContainer = new PIXI.Container();
      var labelsContainer = new PIXI.Container();
      stage.addChild(linkContainer);
      stage.addChild(nodesContainer);
      stage.addChild(labelsContainer);

      var nodeRenderData = [];
      var linkRenderData = [];
      var hoveredNodeId = null;
      var hoveredNeighbours = new Set();
      var dragStartTime = 0;
      var dragging = false;
      var currentTransform = d3.zoomIdentity;

      function nodeRadius(d) {
        var numLinks = 0;
        for (var i = 0; i < graphLinks.length; i++) {
          if (graphLinks[i].source.id === d.id || graphLinks[i].target.id === d.id) {
            numLinks++;
          }
        }
        return (2 + Math.sqrt(numLinks)) * nodeSizeMultiplier;
      }

      function nodeColor(d) {
        if (d.id === slug) {
          return secondary;
        }
        var group = groupColors[d.group || topFolder(d.id)];
        if (group) {
          return group;
        }
        if (visited.has(d.id) || d.id.startsWith("tags/")) {
          return tertiary;
        }
        return gray;
      }

      function updateHoverInfo(newHoveredId) {
        hoveredNodeId = newHoveredId;

        if (newHoveredId === null) {
          hoveredNeighbours = new Set();
          for (var i = 0; i < nodeRenderData.length; i++) {
            nodeRenderData[i].active = false;
          }
          for (var i = 0; i < linkRenderData.length; i++) {
            linkRenderData[i].active = false;
          }
        } else {
          hoveredNeighbours = new Set();

          for (var i = 0; i < linkRenderData.length; i++) {
            var linkData = linkRenderData[i].simulationData;
            if (linkData.source.id === newHoveredId || linkData.target.id === newHoveredId) {
              hoveredNeighbours.add(linkData.source.id);
              hoveredNeighbours.add(linkData.target.id);
              linkRenderData[i].active = true;
            } else {
              linkRenderData[i].active = false;
            }
          }

          hoveredNeighbours.add(newHoveredId);

          for (var i = 0; i < nodeRenderData.length; i++) {
            if (hoveredNeighbours.has(nodeRenderData[i].simulationData.id)) {
              nodeRenderData[i].active = true;
            } else {
              nodeRenderData[i].active = false;
            }
          }
        }
      }

      function renderLinks() {
        for (var i = 0; i < linkRenderData.length; i++) {
          var linkData = linkRenderData[i];
          var alpha = 1;
          if (hoveredNodeId !== null) {
            alpha = linkData.active ? 1 : 0.2;
          }
          linkData.alpha = alpha;
          linkData.color = linkData.active ? gray : lightgray;
        }
      }

      function renderLabels() {
        var defaultScale = 1 / scale;
        var activeScale = defaultScale * 1.1;

        for (var i = 0; i < nodeRenderData.length; i++) {
          var nodeData = nodeRenderData[i];
          if (hoveredNodeId === nodeData.simulationData.id) {
            nodeData.label.alpha = 1;
            nodeData.label.scale.set(activeScale);
          } else {
            nodeData.label.scale.set(defaultScale);
          }
        }
      }

      function renderNodes() {
        for (var i = 0; i < nodeRenderData.length; i++) {
          var nodeData = nodeRenderData[i];
          var alpha = 1;
          if (hoveredNodeId !== null && focusOnHover) {
            alpha = nodeData.active ? 1 : 0.2;
          }
          nodeData.gfx.alpha = alpha;
        }
      }

      function renderPixiFromD3() {
        renderNodes();
        renderLinks();
        renderLabels();
      }

      for (var i = 0; i < nodes.length; i++) {
        var node = nodes[i];
        var nodeId = node.id;
        var isTagNode = nodeId.startsWith("tags/");
        var radius = nodeRadius(node);
        var color = nodeColor(node);

        var label = new PIXI.Text({
          text: node.text,
          style: {
            fontSize: fontSize * 15,
            fill: dark,
            fontFamily: bodyFont,
          },
          resolution: window.devicePixelRatio * 4,
        });
        label.anchor.set(0.5, 1.2);
        label.alpha = 0;
        label.scale.set(1 / scale);
        labelsContainer.addChild(label);

        var gfx = new PIXI.Graphics();
        gfx.circle(0, 0, radius);
        gfx.fill({ color: isTagNode ? light : color });
        if (isTagNode) {
          gfx.stroke({ width: 2, color: tertiary });
        }

        gfx.eventMode = "static";
        gfx.cursor = "pointer";
        gfx.label = nodeId;

        (function (n, g, labelRef) {
          var oldLabelOpacity = 0;
          g.on("pointerover", function (e) {
            updateHoverInfo(n.id);
            oldLabelOpacity = labelRef.alpha;
            if (!dragging) {
              renderPixiFromD3();
            }
          });

          g.on("pointerleave", function () {
            updateHoverInfo(null);
            labelRef.alpha = oldLabelOpacity;
            if (!dragging) {
              renderPixiFromD3();
            }
          });
        })(node, gfx, label);

        nodesContainer.addChild(gfx);

        nodeRenderData.push({
          simulationData: node,
          gfx: gfx,
          label: label,
          color: color,
          alpha: 1,
          active: false,
        });
      }

      for (var i = 0; i < graphLinks.length; i++) {
        var link = graphLinks[i];
        var gfx = new PIXI.Graphics();
        gfx.eventMode = "none";
        linkContainer.addChild(gfx);

        linkRenderData.push({
          simulationData: link,
          gfx: gfx,
          color: lightgray,
          alpha: 1,
          active: false,
        });
      }

      if (enableDrag) {
        var dragSubject = function (event) {
          var mouseX = (event.x - currentTransform.x) / currentTransform.k;
          var mouseY = (event.y - currentTransform.y) / currentTransform.k;

          for (var i = 0; i < nodes.length; i++) {
            var n = nodes[i];
            var dx = mouseX - n.x - width / 2;
            var dy = mouseY - n.y - height / 2;
            var dist = Math.sqrt(dx * dx + dy * dy);
            var rad = nodeRadius(n);
            if (dist < rad + 5) {
              return n;
            }
          }
          return null;
        };

        var dragStarted = function (event) {
          if (!event.active) simulation.alphaTarget(1).restart();
          event.subject.fx = event.subject.x;
          event.subject.fy = event.subject.y;
          var mouseSimX = (event.x - currentTransform.x) / currentTransform.k - width / 2;
          var mouseSimY = (event.y - currentTransform.y) / currentTransform.k - height / 2;
          event.subject.__dragOffset = {
            x: mouseSimX - event.subject.x,
            y: mouseSimY - event.subject.y,
          };
          dragStartTime = Date.now();
          dragging = true;
          hoveredNodeId = event.subject.id;
        };

        var dragDragged = function (event) {
          var mouseSimX = (event.x - currentTransform.x) / currentTransform.k - width / 2;
          var mouseSimY = (event.y - currentTransform.y) / currentTransform.k - height / 2;
          event.subject.fx = mouseSimX - event.subject.__dragOffset.x;
          event.subject.fy = mouseSimY - event.subject.__dragOffset.y;
        };

        var dragEnded = function (event) {
          if (!event.active) simulation.alphaTarget(0);
          event.subject.fx = null;
          event.subject.fy = null;
          dragging = false;
          updateHoverInfo(null);
          renderPixiFromD3();

          if (Date.now() - dragStartTime < 500) {
            var target = resolveBasePath(event.subject.id);
            window.location.href = target;
          }
        };

        var drag = d3
          .drag()
          .container(app.canvas)
          .subject(dragSubject)
          .on("start", dragStarted)
          .on("drag", dragDragged)
          .on("end", dragEnded);

        d3.select(app.canvas).call(drag);
      } else {
        for (var i = 0; i < nodeRenderData.length; i++) {
          (function (nodeData) {
            nodeData.gfx.on("click", function () {
              var target = resolveBasePath(nodeData.simulationData.id);
              window.location.href = target;
            });
          })(nodeRenderData[i]);
        }
      }

      if (enableZoom) {
        var zoomed = function (event) {
          currentTransform = event.transform;
          stage.scale.set(currentTransform.k, currentTransform.k);
          stage.position.set(currentTransform.x, currentTransform.y);

          var newScale = currentTransform.k * opacityScale;
          var scaleOpacity = Math.max((newScale - 1) / 3.75, 0);

          var activeLabels = [];
          for (var i = 0; i < nodeRenderData.length; i++) {
            if (nodeRenderData[i].active) {
              activeLabels.push(nodeRenderData[i].label);
            }
          }

          for (var i = 0; i < labelsContainer.children.length; i++) {
            var label = labelsContainer.children[i];
            if (activeLabels.indexOf(label) === -1) {
              label.alpha = scaleOpacity;
            }
          }
        };

        var zoom = d3
          .zoom()
          .extent([
            [0, 0],
            [width, height],
          ])
          .scaleExtent([0.25, 4])
          .on("zoom", zoomed);

        d3.select(app.canvas).call(zoom);
      }

      var stopAnimation = false;
      function animate() {
        if (stopAnimation) return;

        for (var i = 0; i < nodeRenderData.length; i++) {
          var n = nodeRenderData[i];
          var x = n.simulationData.x;
          var y = n.simulationData.y;
          if (x != null && y != null) {
            n.gfx.position.set(x + width / 2, y + height / 2);
            if (n.label) {
              n.label.position.set(x + width / 2, y + height / 2);
            }
          }
        }

        for (var i = 0; i < linkRenderData.length; i++) {
          var l = linkRenderData[i];
          var linkData = l.simulationData;
          var sx = linkData.source.x;
          var sy = linkData.source.y;
          var tx = linkData.target.x;
          var ty = linkData.target.y;
          if (sx != null && sy != null && tx != null && ty != null) {
            var sX = sx + width / 2;
            var sY = sy + height / 2;
            var tX = tx + width / 2;
            var tY = ty + height / 2;
            l.gfx.clear();
            l.gfx.moveTo(sX, sY);
            l.gfx.lineTo(tX, tY);
            l.gfx.stroke({ alpha: l.alpha, width: 1, color: l.color });

            // Directional arrowhead at the target end, just outside the node.
            if (showArrow) {
              var angle = Math.atan2(tY - sY, tX - sX);
              var gap = nodeRadius(linkData.target) + 1;
              var hx = tX - Math.cos(angle) * gap;
              var hy = tY - Math.sin(angle) * gap;
              var ah = 4;
              l.gfx.moveTo(hx, hy);
              l.gfx.lineTo(
                hx - ah * Math.cos(angle - 0.4),
                hy - ah * Math.sin(angle - 0.4),
              );
              l.gfx.lineTo(
                hx - ah * Math.cos(angle + 0.4),
                hy - ah * Math.sin(angle + 0.4),
              );
              l.gfx.lineTo(hx, hy);
              l.gfx.fill({ alpha: l.alpha, color: l.color });
            }
          }
        }

        requestAnimationFrame(animate);
      }

      simulation.on("tick", function () {});
      simulation.restart();
      renderPixiFromD3();
      animate();

      return function () {
        stopAnimation = true;
        simulation.stop();
        try {
          app.destroy(true);
        } catch (_) {
          // PixiJS may throw if WebGL context was already lost.
        }
      };
    }

    var localCleanups = [];
    var globalCleanups = [];
    var currentRenderGeneration = 0;

    function cleanupLocal() {
      for (var i = 0; i < localCleanups.length; i++) {
        localCleanups[i]();
      }
      localCleanups = [];
    }

    function cleanupGlobal() {
      for (var i = 0; i < globalCleanups.length; i++) {
        globalCleanups[i]();
      }
      globalCleanups = [];
    }

    var globalContainers = [];
    var globalIcons = [];
    var documentClickHandler = null;
    var documentKeydownHandler = null;
    var iconClickHandler = null;

    function hideGlobalGraph() {
      cleanupGlobal();
      for (var i = 0; i < globalContainers.length; i++) {
        globalContainers[i].classList.remove("active");
        var sidebar = globalContainers[i].closest(".sidebar");
        if (sidebar) {
          sidebar.style.zIndex = "";
        }
      }
    }

    function anyGlobalGraphActive() {
      for (var i = 0; i < globalContainers.length; i++) {
        if (globalContainers[i].classList.contains("active")) {
          return true;
        }
      }
      return false;
    }

    function showGlobalGraph() {
      cleanupGlobal();
      var currentSlug = getSlugFromUrl();
      for (var i = 0; i < globalContainers.length; i++) {
        var container = globalContainers[i];
        container.classList.add("active");
        var sidebar = container.closest(".sidebar");
        if (sidebar) {
          sidebar.style.zIndex = "1";
        }

        var graphContainer = container.querySelector(".global-graph-container");
        if (graphContainer) {
          (function (gc) {
            renderGraph(gc, currentSlug, undefined)
              .then(function (cleanup) {
                globalCleanups.push(cleanup);
              })
              .catch(function (err) {
                console.error("[Graph] Global render error:", err);
              });
          })(graphContainer);
        }
      }
    }

    function toggleGlobalGraph() {
      if (anyGlobalGraphActive()) {
        hideGlobalGraph();
      } else {
        showGlobalGraph();
      }
    }

    function renderLocal() {
      cleanupLocal();
      var thisGeneration = ++currentRenderGeneration;
      var slug = getSlugFromUrl();
      addToVisited(slug);

      var localContainers = document.querySelectorAll(".graph-container");
      for (var i = 0; i < localContainers.length; i++) {
        (function (container) {
          renderGraph(container, slug, thisGeneration)
            .then(function (cleanup) {
              if (thisGeneration === currentRenderGeneration) {
                localCleanups.push(cleanup);
              }
            })
            .catch(function (err) {
              console.error("[Graph] Local render error:", err);
            });
        })(localContainers[i]);
      }
    }

    function handleNav(e) {
      var slug = e.detail ? e.detail.url : getSlugFromUrl();
      addToVisited(simplifySlug(slug));

      renderLocal();

      globalContainers = Array.from(document.querySelectorAll(".global-graph-outer"));

      if (iconClickHandler) {
        for (var i = 0; i < globalIcons.length; i++) {
          globalIcons[i].removeEventListener("click", iconClickHandler);
        }
      }

      globalIcons = Array.from(document.querySelectorAll(".global-graph-icon"));
      iconClickHandler = function () {
        toggleGlobalGraph();
      };
      for (var i = 0; i < globalIcons.length; i++) {
        globalIcons[i].addEventListener("click", iconClickHandler);
      }

      if (documentClickHandler) {
        document.removeEventListener("click", documentClickHandler);
      }
      documentClickHandler = function (e) {
        if (anyGlobalGraphActive()) {
          var inContainer = e.target.closest(".global-graph-container");
          var inIcon = e.target.closest(".global-graph-icon");
          if (!inContainer && !inIcon) {
            hideGlobalGraph();
          }
        }
      };
      document.addEventListener("click", documentClickHandler);

      if (documentKeydownHandler) {
        document.removeEventListener("keydown", documentKeydownHandler);
      }
      documentKeydownHandler = function (e) {
        if (e.key === "Escape") {
          if (anyGlobalGraphActive()) {
            hideGlobalGraph();
          }
          return;
        }

        if (e.key === "g" && (e.ctrlKey || e.metaKey) && !e.shiftKey) {
          e.preventDefault();
          toggleGlobalGraph();
        }
      };
      document.addEventListener("keydown", documentKeydownHandler);

      if (anyGlobalGraphActive()) {
        showGlobalGraph();
      }
    }

    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", function () {
        handleNav({ detail: { url: getSlugFromUrl() } });
      });
    } else {
      handleNav({ detail: { url: getSlugFromUrl() } });
    }
    document.addEventListener("prenav", function () {
      cleanupLocal();
      cleanupGlobal();
    });
    document.addEventListener("nav", handleNav);
    document.addEventListener("render", handleNav);

    function handleThemeChange() {
      renderLocal();
      if (anyGlobalGraphActive()) {
        showGlobalGraph();
      }
    }
    document.addEventListener("themechange", handleThemeChange);
  }
})();
