# ClearGlass Loading Screen

Two implementations of the same design:

- **`LoadingScreen.tsx`** — React + Tailwind + Framer Motion (production)
- **`index.html`** — vanilla HTML/CSS/JS (drop-in, zero dependencies)

Open `index.html` in a browser to preview. Both render the same UI:
hexagonal CG monogram, deep red neon, animated progress 0–100%,
classified-style microtext, soft flicker, scan line, vignette.

## React usage

Requires `react`, `framer-motion`, and Tailwind configured in your app.

```tsx
import LoadingScreen from "./LoadingScreen";

export default function App() {
  const [ready, setReady] = useState(false);
  return ready
    ? <YourApp />
    : <LoadingScreen onComplete={() => setReady(true)} />;
}
```

Props:

| Prop | Default | Notes |
|---|---|---|
| `brand` | `"CLEARGLASS"` | Top-left wordmark |
| `monogram` | `"CG"` | Center logo letters |
| `durationMs` | `4200` | Fill animation length |
| `onComplete` | — | Fires when progress hits 100 |

Respects `prefers-reduced-motion` (no rotation, flicker, or scan line).
Accessible: `role="status"`, `aria-live`, screen-reader percentage label.

## Standalone HTML usage

`index.html` is fully self-contained. To use as a real loading screen:

```html
<iframe src="loading.html" id="loader"></iframe>
<script>
  // hide when your app is ready
  document.getElementById("loader").style.display = "none";
</script>
```

Or copy the markup + style + script blocks directly into your shell.
