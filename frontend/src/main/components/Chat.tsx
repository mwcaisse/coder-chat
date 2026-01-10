import { IconButton, Stack, TextField, Box } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import { FormEvent, useLayoutEffect, useRef, useState } from "react";
import EmptyChatPrompt from "@app/components/EmptyChatPrompt.tsx";
import {
    ChatMessage,
    ChatMessageLoading,
} from "@app/components/ChatMessage.tsx";
import { useChatContext } from "@app/components/ChatContext.tsx";

export default function Chat() {
    const {
        messages,
        loadingMessageResponse,
        inProcessMessageResponse,
        sendMessage,
    } = useChatContext();

    const [currentMessage, setCurrentMessage] = useState("");

    const chatBoxRef = useRef<HTMLDivElement>(null);
    const [chatBoxHeight, setChatBoxHeight] = useState<number>(100);

    useLayoutEffect(() => {
        const updateHeight = () => {
            if (chatBoxRef.current) {
                const { height } = chatBoxRef.current.getBoundingClientRect();
                setChatBoxHeight(height);
            }
        };

        updateHeight();

        window.addEventListener("resize", updateHeight);

        return () => window.removeEventListener("resize", updateHeight);
    }, []);

    const onSubmit = (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        if (currentMessage.length === 0) return;
        sendMessage(currentMessage);
        setCurrentMessage("");
    };

    return (
        <Box>
            {messages.length === 0 && (
                <EmptyChatPrompt
                    currentMessage={currentMessage}
                    setCurrentMessage={setCurrentMessage}
                    onSubmit={onSubmit}
                />
            )}
            {messages.length !== 0 && (
                <Box flexGrow={1}>
                    <Stack
                        direction="column-reverse"
                        spacing={1}
                        sx={{
                            height: `calc(100vh - ${chatBoxHeight + 40}px)`,
                            overflowY: "auto",
                        }}
                    >
                        {loadingMessageResponse &&
                            inProcessMessageResponse.length === 0 && (
                                <Box
                                    sx={{
                                        display: "flex",
                                        flexDirection: "row",
                                        justifyContent: "flex-start",
                                        maxWidth: "100%",
                                    }}
                                >
                                    <ChatMessageLoading />
                                </Box>
                            )}
                        {inProcessMessageResponse.length > 0 && (
                            <Box
                                sx={{
                                    display: "flex",
                                    flexDirection: "row",
                                    justifyContent: "flex-start",
                                    maxWidth: "100%",
                                }}
                            >
                                <ChatMessage
                                    content={inProcessMessageResponse.join("")}
                                />
                            </Box>
                        )}
                        {messages
                            .slice()
                            .reverse()
                            .map((message, index) => (
                                <Box
                                    key={index}
                                    sx={{
                                        display: "flex",
                                        flexDirection: "row",
                                        justifyContent: message.from_user
                                            ? "flex-end"
                                            : "flex-start",
                                        maxWidth: "100%",
                                    }}
                                >
                                    <ChatMessage content={message.content} />
                                </Box>
                            ))}
                    </Stack>
                    <Box
                        sx={{
                            position: "fixed",
                            bottom: 10,
                            width: "100%",
                            maxWidth: "lg",
                        }}
                        ref={chatBoxRef}
                    >
                        <form onSubmit={onSubmit}>
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
                                    onChange={(e) =>
                                        setCurrentMessage(e.target.value)
                                    }
                                />
                                <IconButton size="large" type="submit">
                                    <SendIcon />
                                </IconButton>
                            </Stack>
                        </form>
                    </Box>
                </Box>
            )}
        </Box>
    );
}
