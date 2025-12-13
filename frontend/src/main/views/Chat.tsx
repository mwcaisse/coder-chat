import {IconButton, Container, Stack, TextField} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import {useState} from "react";

export default function Chat() {

    const [currentMessage, setCurrentMessage] = useState("");

    return (
        <Container sx={{pt: 2}}>
            <Stack direction="row" spacing={1}>
                <TextField
                    variant="outlined"
                    fullWidth
                    slotProps={{
                        input: {
                            sx: {borderRadius: 5}
                        }
                    }}
                    placeholder="Ask coder chat"
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                />
                <IconButton size="large"><SendIcon /></IconButton>
            </Stack>
        </Container>
    );
}