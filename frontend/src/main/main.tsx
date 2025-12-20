import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "@app/App.tsx";

// Roboto Fonts
import "@fontsource/roboto/300.css";
import "@fontsource/roboto/400.css";
import "@fontsource/roboto/500.css";
import "@fontsource/roboto/700.css";

// Even though webstorm doesn't like this, this works
// @ts-expect-error this appeases the build when .css is included, but it fails to run when .css is included..
import "@wooorm/starry-night/style/dark";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <App />
    </StrictMode>,
);
