import { IconButton, Stack, TextField, Box } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import { FormEvent } from "react";

type EmptyChatPromptProps = {
    onSubmit: (event: FormEvent<HTMLFormElement>) => void;
    currentMessage: string;
    setCurrentMessage: (message: string) => void;
};

export default function EmptyChatPrompt({
    onSubmit,
    currentMessage,
    setCurrentMessage,
}: EmptyChatPromptProps) {
    return (
        <Box
            display="flex"
            alignItems="center"
            justifyContent="center"
            sx={{ height: "100vh" }}
        >
            <form onSubmit={onSubmit}>
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
            </form>
        </Box>
    );
}
