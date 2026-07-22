{
  "brand": {
    "name": "AI Stack Console",
    "personality": [
      "engineering-console",
      "trustworthy",
      "precise",
      "calm-high-contrast",
      "copy-paste-first"
    ],
    "north_star": "Make a Docker Compose stack feel as reliable as a CI report: clear architecture, explicit constraints, and one-click copy/download ergonomics."
  },
  "layout": {
    "page_type": "single-page dashboard with anchored sections",
    "grid": {
      "container": "max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8",
      "section_spacing": "py-10 sm:py-14",
      "desktop_split": "lg:grid lg:grid-cols-12 lg:gap-8",
      "sidebar_cols": "lg:col-span-4",
      "main_cols": "lg:col-span-8",
      "bento_rule": "Use bento cards for Overview + Ports + Fixes; keep code viewer full-width on desktop split (sidebar list + main code panel)."
    },
    "nav": {
      "pattern": "sticky top nav with section anchors + active section highlight",
      "classes": "sticky top-0 z-40 border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60",
      "active_indicator": "left border accent + subtle bg",
      "smooth_scroll": "Use CSS scroll-behavior: smooth on html; respect prefers-reduced-motion"
    },
    "sections": [
      "Overview/Hero",
      "Architecture",
      "Ports",
      "Fixes Applied",
      "Files (viewer)",
      "Validation Report",
      "Quick Start"
    ]
  },
  "typography": {
    "font_pairing": {
      "ui": {
        "google_font": "IBM Plex Sans",
        "fallback": "ui-sans-serif, system-ui",
        "usage": "All UI labels, headings, tables"
      },
      "mono": {
        "google_font": "JetBrains Mono",
        "fallback": "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas",
        "usage": "Code viewer, snippets, port mappings, badges with numbers"
      }
    },
    "scale_tailwind": {
      "h1": "text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight",
      "h2": "text-base md:text-lg font-medium text-muted-foreground",
      "section_title": "text-xl sm:text-2xl font-semibold tracking-tight",
      "body": "text-sm sm:text-base leading-relaxed",
      "small": "text-xs sm:text-sm",
      "mono": "font-mono text-xs sm:text-sm leading-6"
    },
    "content_density": "Prefer compact but breathable: increase whitespace (gap-6/8) rather than shrinking type below text-sm."
  },
  "color_system": {
    "mode": "dark-first (console) with light surfaces for code readability inside panels",
    "gradient_policy": {
      "allowed": "Only as a subtle decorative overlay in hero background (<=20% viewport).",
      "forbidden": "No saturated purple/pink gradients; no gradients on code blocks, tables, or reading-heavy areas."
    },
    "tokens_css_variables": {
      "note": "Map these into /src/index.css :root and .dark. Keep shadcn variable names but replace values.",
      "dark": {
        "--background": "215 35% 8%",
        "--foreground": "210 20% 98%",
        "--card": "215 32% 11%",
        "--card-foreground": "210 20% 98%",
        "--popover": "215 32% 11%",
        "--popover-foreground": "210 20% 98%",
        "--primary": "168 70% 42%",
        "--primary-foreground": "210 20% 98%",
        "--secondary": "215 25% 16%",
        "--secondary-foreground": "210 20% 98%",
        "--muted": "215 22% 16%",
        "--muted-foreground": "215 12% 70%",
        "--accent": "168 70% 42%",
        "--accent-foreground": "210 20% 98%",
        "--destructive": "0 72% 52%",
        "--destructive-foreground": "210 20% 98%",
        "--border": "215 18% 22%",
        "--input": "215 18% 22%",
        "--ring": "168 70% 42%",
        "--radius": "0.75rem"
      },
      "light": {
        "--background": "210 25% 98%",
        "--foreground": "215 25% 12%",
        "--card": "0 0% 100%",
        "--card-foreground": "215 25% 12%",
        "--popover": "0 0% 100%",
        "--popover-foreground": "215 25% 12%",
        "--primary": "168 70% 34%",
        "--primary-foreground": "0 0% 100%",
        "--secondary": "210 20% 96%",
        "--secondary-foreground": "215 25% 12%",
        "--muted": "210 20% 96%",
        "--muted-foreground": "215 12% 40%",
        "--accent": "168 70% 34%",
        "--accent-foreground": "0 0% 100%",
        "--destructive": "0 72% 52%",
        "--destructive-foreground": "0 0% 100%",
        "--border": "215 16% 88%",
        "--input": "215 16% 88%",
        "--ring": "168 70% 34%",
        "--radius": "0.75rem"
      },
      "extended_tokens": {
        "--canvas": "#0b1320",
        "--panel": "#101827",
        "--panel-2": "#151f2e",
        "--code-bg": "#05070c",
        "--code-border": "rgba(243,245,244,0.12)",
        "--code-fg": "#e5e7eb",
        "--code-muted": "#94a3b8",
        "--success": "#16a34a",
        "--warning": "#d97706",
        "--danger": "#dc2626",
        "--info": "#0ea5e9"
      }
    },
    "component_color_rules": {
      "cards": "Use card bg (dark) with subtle border; avoid heavy shadows.",
      "tables": "Row hover uses muted bg; borders are 1px subtle.",
      "badges": {
        "pass": "bg-[color:var(--success)]/15 text-[color:var(--success)] border-[color:var(--success)]/25",
        "fail": "bg-[color:var(--danger)]/15 text-[color:var(--danger)] border-[color:var(--danger)]/25",
        "warn": "bg-[color:var(--warning)]/15 text-[color:var(--warning)] border-[color:var(--warning)]/25",
        "info": "bg-[color:var(--info)]/15 text-[color:var(--info)] border-[color:var(--info)]/25"
      }
    }
  },
  "components": {
    "component_path": {
      "button": "/app/frontend/src/components/ui/button.jsx",
      "card": "/app/frontend/src/components/ui/card.jsx",
      "badge": "/app/frontend/src/components/ui/badge.jsx",
      "tabs": "/app/frontend/src/components/ui/tabs.jsx",
      "table": "/app/frontend/src/components/ui/table.jsx",
      "scroll_area": "/app/frontend/src/components/ui/scroll-area.jsx",
      "separator": "/app/frontend/src/components/ui/separator.jsx",
      "sheet": "/app/frontend/src/components/ui/sheet.jsx",
      "tooltip": "/app/frontend/src/components/ui/tooltip.jsx",
      "skeleton": "/app/frontend/src/components/ui/skeleton.jsx",
      "sonner_toast": "/app/frontend/src/components/ui/sonner.jsx",
      "progress": "/app/frontend/src/components/ui/progress.jsx",
      "collapsible": "/app/frontend/src/components/ui/collapsible.jsx",
      "accordion": "/app/frontend/src/components/ui/accordion.jsx",
      "command": "/app/frontend/src/components/ui/command.jsx"
    },
    "buttons": {
      "style": "Professional / Corporate with slight console edge",
      "radius": "rounded-xl",
      "primary": {
        "classes": "bg-primary text-primary-foreground hover:bg-primary/90 focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
        "micro": "hover: translateY(-1px) via shadow change only; active: scale-[0.98]"
      },
      "secondary": {
        "classes": "bg-secondary text-secondary-foreground hover:bg-secondary/80 border border-border",
        "micro": "hover border brightens; active scale"
      },
      "ghost": {
        "classes": "hover:bg-accent/10 hover:text-foreground",
        "micro": "underline appears on hover for link-like actions"
      },
      "icon_button": {
        "classes": "h-9 w-9 rounded-lg border border-border bg-card hover:bg-muted",
        "usage": "Copy, Download, Expand"
      }
    },
    "hero": {
      "layout": "Left: title/value prop + CTAs; Right: mini status + constraints chips",
      "background": "Solid canvas with a subtle teal radial overlay (<=20% viewport) + noise",
      "chips": "Use Badge for constraints: 'Ports 3000/4000 blocked', 'OpenHands on :5000', 'Headroom on :5001'"
    },
    "architecture_diagram": {
      "approach": "SVG-based diagram inside a Card (no heavy libs). Use consistent stroke widths and tokens.",
      "visual_treatment": {
        "nodes": "Rounded rectangles with subtle border; service icon + name + key mounts/ports",
        "edges": "1.5px lines with arrowheads; teal for primary flow, muted for secondary",
        "network_pill": "Centered pill labeled 'ai-stack-network'",
        "callouts": "Small mono labels for port mapping and mounts"
      },
      "tailwind_classes": {
        "canvas": "w-full overflow-hidden rounded-xl border bg-card",
        "svg": "w-full h-[320px] sm:h-[360px]",
        "node": "fill-[hsl(var(--card))] stroke-[hsl(var(--border))]",
        "edge_primary": "stroke-[hsl(var(--primary))]",
        "edge_muted": "stroke-[hsl(var(--muted-foreground))]"
      }
    },
    "ports_table": {
      "pattern": "Table with explicit forbidden ports row",
      "columns": ["Service", "Host Port", "Container Port", "Notes"],
      "row_highlight": "Forbidden ports row uses destructive badge + muted background"
    },
    "fixes_applied": {
      "pattern": "Two feature cards with icon, short explanation, and a compact code snippet",
      "snippet": "Use ScrollArea + pre + code; include Copy button",
      "icons": "lucide-react: ShieldCheck (socket perms), Network (dind networking)"
    },
    "file_viewer": {
      "layout": "Desktop: resizable split (left file list, right code panel). Mobile: Tabs (Files / Preview).",
      "use": ["resizable", "scroll-area", "tabs", "badge", "button", "skeleton"],
      "file_list": {
        "item": "button-like row with filename + type badge + modified dot",
        "active": "bg-accent/10 border-l-2 border-primary",
        "search": "Command component as quick file search (Cmd+K)"
      },
      "code_panel": {
        "header": "Filename + language badge + line count + Copy/Download",
        "body": "ScrollArea with code theme",
        "code_classes": "rounded-xl border bg-[color:var(--code-bg)] text-[color:var(--code-fg)]"
      },
      "syntax_highlighting": {
        "library": "react-syntax-highlighter",
        "install": "npm i react-syntax-highlighter",
        "theme": "Use a dark theme (e.g., oneDark) but override background to --code-bg and ensure contrast.",
        "line_numbers": "Show line numbers; keep them muted"
      }
    },
    "validation_panel": {
      "pattern": "CI-style checklist with summary header + filters",
      "header": "Progress bar + counts (Pass/Fail/Warn) + last run timestamp",
      "list": "Accordion grouped by category (Ports, Networking, Volumes, Security, Compose hygiene)",
      "item": "Row with status icon + check name + optional 'why it matters' tooltip",
      "empty_loading_error": {
        "loading": "Skeleton rows",
        "empty": "Muted callout with retry button",
        "error": "Alert with error details + 'Retry'"
      }
    },
    "quick_start": {
      "pattern": "Numbered steps in Cards + a troubleshooting callout",
      "callout": "Alert component with 'If Docker socket group mismatch...'"
    }
  },
  "motion": {
    "library": {
      "optional": "framer-motion",
      "install": "npm i framer-motion",
      "usage": "Entrance animations for sections (fade+slide 8px), hover lift for cards, copy feedback micro-anim"
    },
    "principles": [
      "No universal transition: never transition: all",
      "Use 150-220ms for hover, 90-120ms for active",
      "Respect prefers-reduced-motion",
      "Use subtle transforms only on small elements (buttons/cards), not on code blocks"
    ],
    "micro_interactions": {
      "copy": "On copy: icon swaps to check for 1.2s + sonner toast 'Copied'.",
      "download": "On download: subtle progress indicator (spinner) if async.",
      "nav": "Active anchor highlights as you scroll (IntersectionObserver).",
      "validation": "When checks refresh: shimmer skeleton then replace; animate progress bar width"
    }
  },
  "accessibility": {
    "requirements": [
      "WCAG AA contrast for text on backgrounds",
      "Visible focus rings (ring + ring-offset)",
      "Keyboard navigable file list and tabs",
      "Use aria-label on icon-only buttons",
      "Prefer semantic headings and landmarks"
    ],
    "reduced_motion": "Disable parallax/entrance animations when prefers-reduced-motion: reduce"
  },
  "testing": {
    "data_testid_rules": {
      "convention": "kebab-case describing role",
      "must_apply_to": [
        "primary CTAs",
        "nav anchor links",
        "file list items",
        "copy/download buttons",
        "validation refresh button",
        "validation status summary",
        "port table rows",
        "error callouts"
      ],
      "examples": [
        "data-testid=\"hero-copy-quickstart-button\"",
        "data-testid=\"hero-download-zip-button\"",
        "data-testid=\"files-filelist-item-docker-compose\"",
        "data-testid=\"codepanel-copy-button\"",
        "data-testid=\"validation-refresh-button\"",
        "data-testid=\"ports-forbidden-ports-row\""
      ]
    }
  },
  "images": {
    "image_urls": [
      {
        "category": "hero-background-overlay",
        "description": "Optional subtle decorative background image (use with opacity 0.06-0.10 + mask). Keep under 20% viewport impact.",
        "url": "https://images.pexels.com/photos/14297430/pexels-photo-14297430.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
      },
      {
        "category": "empty-state-illustration",
        "description": "Use as a tiny thumbnail in empty states (max 120px wide) with grayscale + low opacity.",
        "url": "https://images.unsplash.com/photo-1602621186767-c51b537e7543?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85"
      }
    ]
  },
  "implementation_notes_js": {
    "react_files": "Project uses .js (not .tsx). Keep components in JS and use prop-types only if already present.",
    "icons": "Use lucide-react icons (no emoji).",
    "code_copy": {
      "snippet": "navigator.clipboard.writeText(code).then(() => toast.success('Copied'))",
      "toast": "Use sonner (already in /components/ui/sonner.jsx)"
    },
    "code_viewer_scaffold": {
      "structure": [
        "<Tabs> for mobile",
        "<ResizablePanelGroup> for desktop",
        "<ScrollArea> wrapping <SyntaxHighlighter>"
      ]
    }
  },
  "instructions_to_main_agent": [
    "Replace default CRA App.css centering styles; do not center the entire app container.",
    "Adopt dark-first console theme by setting .dark on html/body (or app root) and updating CSS variables in index.css.",
    "Implement sticky anchor nav with active section highlight; ensure each anchor link has data-testid.",
    "Architecture diagram: implement as inline SVG inside Card; keep labels monospace; include port mapping callouts.",
    "File viewer: desktop resizable split; mobile tabs. Add Copy/Download icon buttons with tooltips and sonner toasts.",
    "Validation panel: CI-style grouped checklist with progress summary; use Badge variants for pass/fail/warn.",
    "Use react-syntax-highlighter for code; ensure code background uses --code-bg and never gradients.",
    "Every interactive element and key info element must include data-testid (kebab-case)."
  ],
  "general_ui_ux_design_guidelines": "\n    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms\n    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text\n   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json\n\n **GRADIENT RESTRICTION RULE**\nNEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc\nNEVER use dark gradients for logo, testimonial, footer etc\nNEVER let gradients cover more than 20% of the viewport.\nNEVER apply gradients to text-heavy content or reading areas.\nNEVER use gradients on small UI elements (<100px width).\nNEVER stack multiple gradient layers in the same viewport.\n\n**ENFORCEMENT RULE:**\n    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors\n\n**How and where to use:**\n   • Section backgrounds (not content backgrounds)\n   • Hero section header content. Eg: dark to light to dark color\n   • Decorative overlays and accent elements only\n   • Hero section with 2-3 mild color\n   • Gradients creation can be done for any angle say horizontal, vertical or diagonal\n\n- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**\n\n</Font Guidelines>\n\n- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. \n   \n- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.\n\n- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.\n   \n- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly\n    Eg: - if it implies playful/energetic, choose a colorful scheme\n           - if it implies monochrome/minimal, choose a black–white/neutral scheme\n\n**Component Reuse:**\n\t- Prioritize using pre-existing components from src/components/ui when applicable\n\t- Create new components that match the style and conventions of existing components when needed\n\t- Examine existing components to understand the project's component patterns before creating new ones\n\n**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component\n\n**Best Practices:**\n\t- Use Shadcn/UI as the primary component library for consistency and accessibility\n\t- Import path: ./components/[component-name]\n\n**Export Conventions:**\n\t- Components MUST use named exports (export const ComponentName = ...)\n\t- Pages MUST use default exports (export default function PageName() {...})\n\n**Toasts:**\n  - Use `sonner` for toasts\"\n  - Sonner component are located in `/app/src/components/ui/sonner.tsx`\n\nUse 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals.\n"
}
