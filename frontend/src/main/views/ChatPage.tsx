import { Box, Stack } from "@mui/material";
import Chat from "@app/components/Chat.tsx";

import ChatLeftMenu from "@app/components/ChatLeftMenu.tsx";

export default function ChatPage() {
    return (
        <Stack direction="row">
            <ChatLeftMenu />
            <Box flexGrow={1}>
                <Chat />
            </Box>
        </Stack>
    );
}
