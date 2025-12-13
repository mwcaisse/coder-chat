import {
    IconButton,
    Container,
    Stack,
    TextField,
    Paper,
    Box,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import { FormEvent, useState } from "react";

export default function Chat() {
    const [messages, setMessages] = useState<string[]>([]);
    const [currentMessage, setCurrentMessage] = useState("");

    const obSubmit = (event: FormEvent<HTMLFormElement>) => {
        setMessages((prev) => [...prev, currentMessage]);
        setCurrentMessage("");

        event.preventDefault();
    };

    return (
        <Container sx={{ pt: 2 }}>
            <Stack direction="column" spacing={2}>
                <Stack direction="column" spacing={1}>
                    {messages.map((message, index) => (
                        <Box
                            key={index}
                            sx={{
                                display: "flex",
                                flexDirection: "row",
                                justifyContent:
                                    index % 2 === 0 ? "flex-end" : "flex-start",
                            }}
                        >
                            <Paper sx={{ p: 2, borderRadius: 5 }}>
                                {message}
                            </Paper>
                        </Box>
                    ))}
                </Stack>
                <form onSubmit={obSubmit}>
                    <Stack direction="row" spacing={1}>
                        <TextField
                            variant="outlined"
                            fullWidth
                            slotProps={{
                                input: {
                                    sx: { borderRadius: 5 },
                                },
                            }}
                            placeholder="Ask coder chat"
                            value={currentMessage}
                            onChange={(e) => setCurrentMessage(e.target.value)}
                        />
                        <IconButton size="large" type="submit">
                            <SendIcon />
                        </IconButton>
                    </Stack>
                </form>
            </Stack>
        </Container>
    );
}
