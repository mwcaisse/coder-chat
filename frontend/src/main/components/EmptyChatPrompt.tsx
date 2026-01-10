import { IconButton, Stack, TextField, Box, Autocomplete } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import { FormEvent, useState } from "react";
import { useChatContext } from "@app/components/ChatContext.tsx";

const languages = ["Python", "C#", "TypeScript", "JavaScript"];

export default function EmptyChatPrompt() {
    const { createChatWithMessage } = useChatContext();

    const [currentMessage, setCurrentMessage] = useState("");
    const [language, setLanguage] = useState<string | null>(languages[0]);

    const onSubmit = (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        if (currentMessage.length === 0) return;

        createChatWithMessage(currentMessage, language);
        setCurrentMessage("");
    };

    return (
        <Box
            display="flex"
            alignItems="center"
            justifyContent="center"
            sx={{ height: "100vh" }}
        >
            <form onSubmit={onSubmit}>
                <Stack direction="column" spacing={1}>
                    <Stack direction="row" spacing={1}>
                        <TextField
                            variant="outlined"
                            fullWidth
                            sx={{
                                minWidth: "60vw",
                            }}
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
                    <Autocomplete
                        disablePortal
                        renderInput={(params) => (
                            <TextField {...params} label="Language" />
                        )}
                        sx={{ width: 300 }}
                        options={languages}
                        size="small"
                        value={language}
                        onChange={(_, newValue: string | null) =>
                            setLanguage(newValue)
                        }
                    />
                </Stack>
            </form>
        </Box>
    );
}
