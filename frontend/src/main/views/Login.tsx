import {
    Box,
    Button,
    Container,
    Stack,
    TextField,
    Typography,
} from "@mui/material";
import { FormEvent, useState } from "react";
import ky, { HTTPError } from "ky";
import { useToastContext } from "@app/contexts/ToastContext.tsx";

type LoginResponse = {
    access_token: string;
    refresh_token: string;
};

const submitLogin = async (
    username: string,
    password: string,
): Promise<LoginResponse> => {
    return await ky
        .post("/api/user/login/", {
            json: {
                username,
                password,
            },
        })
        .json();
};

export default function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [errorMessage, setErrorMessage] = useState<string | null>(null);

    const toast = useToastContext();

    const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setErrorMessage(null);
        try {
            const resp = await submitLogin(username, password);
            // TODO: Navigate to chat
        } catch (e) {
            setPassword("");
            console.dir(e);
            if (e instanceof HTTPError && e.response.status == 401) {
                const err_resp = await e.response.json();
                setErrorMessage(err_resp.error);
            } else {
                toast.showError("Login failed");
            }
        }
    };

    return (
        <Container sx={{ pt: 2 }}>
            <Box
                display="flex"
                flexDirection="column"
                alignItems="center"
                justifyContent="center"
                sx={{ minHeight: "98vh" }}
            >
                <Box sx={{ pt: 2, minWidth: "450px" }}>
                    <form onSubmit={onSubmit}>
                        <Stack direction="column" spacing={2}>
                            <Typography variant="h3">Coder Chat</Typography>
                            <Typography variant="h5">Login</Typography>
                            <TextField
                                label="Username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                            />
                            <TextField
                                label="Password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                            {errorMessage && (
                                <Typography variant="caption" color="error">
                                    {errorMessage}
                                </Typography>
                            )}
                            <Stack direction="row" justifyContent="flex-end">
                                <Button variant="contained" type="submit">
                                    Login
                                </Button>
                            </Stack>
                        </Stack>
                    </form>
                </Box>
            </Box>
        </Container>
    );
}
