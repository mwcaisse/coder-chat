import {createTheme, CssBaseline, ThemeProvider} from "@mui/material";
import Chat from "@app/views/Chat";


const theme = createTheme({
    palette: {
        mode: "dark",
    },
});

function App() {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <Chat />
        </ThemeProvider>
    );
}

export default App;
