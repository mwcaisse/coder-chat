import { Box, Stack } from "@mui/material";
import Chat from "@app/components/Chat.tsx";

import ChatLeftMenu from "@app/components/ChatLeftMenu.tsx";
import { ChatContextProvider } from "@app/components/ChatContext.tsx";

export default function ChatPage() {
    return (
        <ChatContextProvider>
            <Stack direction="row">
                <ChatLeftMenu />
                <Box flexGrow={1} sx={{ ml: 2, py: 2, px: 3 }}>
                    <Chat />
                </Box>
            </Stack>
        </ChatContextProvider>
    );
}
