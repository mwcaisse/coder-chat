import { createTheme, CssBaseline, ThemeProvider } from "@mui/material";
import Login from "@app/views/Login.tsx";
import { ToastContextProvider } from "@app/contexts/ToastContext.tsx";
import { SnackbarProvider } from "notistack";
import { createBrowserRouter, RouterProvider } from "react-router";
import { ProtectedRoute, UnauthedRoute } from "@app/ProtectedRoute.tsx";
import ChatPage from "@app/views/ChatPage.tsx";

const theme = createTheme({
    palette: {
        mode: "dark",
    },
});

const router = createBrowserRouter([
    {
        path: "/login",
        element: (
            <UnauthedRoute>
                <Login />
            </UnauthedRoute>
        ),
    },
    {
        path: "/",
        element: (
            <ProtectedRoute>
                <ChatPage />
            </ProtectedRoute>
        ),
    },
]);

function App() {
    return (
        <ThemeProvider theme={theme}>
            <SnackbarProvider>
                <ToastContextProvider>
                    <CssBaseline />
                    <RouterProvider router={router} />
                </ToastContextProvider>
            </SnackbarProvider>
        </ThemeProvider>
    );
}

export default App;
