import { createTheme, CssBaseline, ThemeProvider } from "@mui/material";
import Login from "@app/views/Login.tsx";
import { ToastContextProvider } from "@app/contexts/ToastContext.tsx";
import { SnackbarProvider } from "notistack";

const theme = createTheme({
    palette: {
        mode: "dark",
    },
});

function App() {
    return (
        <ThemeProvider theme={theme}>
            <SnackbarProvider>
                <ToastContextProvider>
                    <CssBaseline />
                    {/*<Chat />*/}
                    <Login />
                </ToastContextProvider>
            </SnackbarProvider>
        </ThemeProvider>
    );
}

export default App;
